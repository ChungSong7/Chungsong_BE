from rest_framework import serializers
from django.shortcuts import get_object_or_404
from users.authentications import extract_user_from_jwt

from users.serializers import NoticeSerializer
from posts.models import Post,Comment,Commenter
from users.models import Notice,User
from rest_framework.exceptions import APIException

class CommentSerializer(serializers.ModelSerializer):
    anon_status = serializers.BooleanField(required=True)
    commenter_profile=serializers.SerializerMethodField(required=False) 
    post= serializers.UUIDField(required=False)
    commenter= serializers.CharField(required=False)
    writer_id=serializers.UUIDField(source='writer.user_id',required=False)

    class Meta:
        model = Comment
        fields = ['comment_id', 'post','up_comment_id', 'content', 'created_at', 'anon_status','writer_id',
                'commenter', 'like_size', 'warn_size','display','commenter_profile']
        #'anon_status', 'anon_num',
    
    def get_writer_id(self,obj):
        return object.writer.user_id
    
    def get_commenter_profile(self,obj):
        post = obj.post
        if obj.commenter=='글쓴이':
            return obj.post.author_profile
        elif obj.anon_status:  # 익명 기작성자.
            commenter = post.commenters.get(user=obj.writer, anon_num__gt=0)
            return commenter.anon_num
        else:  # not obj.anon_status: #별명 기작성자
            return obj.writer.profile_image
    '''
        try:
            post = obj.post
            if obj.commenter=='글쓴이':
                return obj.post.author_profile
            elif obj.anon_status:  # 익명 기작성자.
                print('ok0')
                commenter = post.commenters.get(user=obj.writer, anon_num__gt=0)
                print('ok1')
                return commenter.anon_num
            else:  # not obj.anon_status: #별명 기작성자
                print('ok2')
                return obj.writer.profile_image
        except Commenter.DoesNotExist:
            print('찾지 못한 commenter user: ',obj.writer_id)
            print(obj)
        except APIException as e:
            # 예외 처리 로직을 여기에 추가합니다.
            # 예를 들어 로깅이나 사용자에게 적절한 오류 메시지를 반환할 수 있습니다.
            print(f"An API exception occurred: {str(e)}")
            comments_data = []
    '''


    def create(self, validated_data):
        #images_data = validated_data.pop('images', None)
        post_id = self.context['post_id'] #url에 담겨있
        post = get_object_or_404(Post, post_id=post_id)
        user=extract_user_from_jwt(self.context['request'])

        comment_data = {
            'post': post, #게시판 객체.이름
            'up_comment_id':self.context['up_comment_id'], #어미 댓글
            'writer':user, #댓글 작성자 FK
            'content': validated_data['content'],
            'commenter': self.context['commenter'], #별명? 아님 익명2?
            'anon_status': validated_data.get('anon_status'),
        }
        # 댓글 생성
        comment = Comment.objects.create(**comment_data)
        
        #post 댓글 수 ++
        post.comment_size = Comment.objects.filter(post=post, display=True).count()
        post.save()

        #게시글 주인 아닌데 댓글을 달았다:: 게시글 주인한테 알림 생성
        if comment.writer!=post.author:
            notice_data = {
                'user': post.author,  # 게시글 작성자
                'root_id': comment.comment_id,  # 댓글의 고유 ID
                'category': '댓글',  # 알림 카테고리
            }
            Notice.objects.create(**notice_data)
        #어미댓글 있는데 나 아니면, 어미댓 주인한테 알림.
        if comment.up_comment_id:
            up_comment=get_object_or_404(Comment,comment_id=comment.up_comment_id)
            if comment.writer != up_comment.writer:
                notice_data={
                    'user':up_comment.writer, #어미댓 작성자
                    'root_id':comment.comment_id, #대댓글 고유 ID
                    'category':'대댓글', #알림 카테고리
                }
                Notice.objects.create(**notice_data)
        return comment
    

def get_comments_with_replies(post_id):
    comments = Comment.objects.filter(post_id=post_id, up_comment_id__isnull=True).order_by('created_at')
    response_data = []

    for comment in comments:
        response_data.append(serialize_comment(comment))

        replies = Comment.objects.filter(post_id=comment.post_id, up_comment_id=comment.comment_id).order_by('created_at')
        for reply in replies:
            response_data.append(serialize_comment(reply))
    return response_data

def serialize_comment(comment):
    serializer = CommentSerializer(comment)
    return serializer.data

'''
def serialize_replies(comment):
    replies = Comment.objects.filter(post_id=comment.post_id, up_comment_id=comment.comment_id).order_by('created_at')
    print(comment ,'의 replies')
    print(replies)
    serialized_replies = []

    for reply in replies:
        serialized_replies.append(serialize_comment(reply))
    print(serialized_replies)

    return serialized_replies
'''