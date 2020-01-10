from django.http import Http404
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from apps.blog.serializers import *
from apps.blog import paginations


# Create your views here.

class BlogView(GenericAPIView):
    serializer_class = PostDescriptionSerializer
    queryset = Post.objects.all().order_by('-date')

    def get(self, request):
        descriptions = PostDescriptionSerializer(self.get_queryset(), many=True)
        return Response(descriptions.data)


class PostView(GenericAPIView):
    serializer_class = PostSerializer
    queryset = Post.objects.all()

    def get(self, request, post_id):
        try:
            data = PostSerializer(self.get_queryset().get(pk=post_id)).data
            return Response(data)
        except Post.DoesNotExist:
            raise Http404


class CommentListView(GenericAPIView):
    serializer_class = PostCommentSerializer
    queryset = Comment.objects.all().order_by('-date')
    permission_classes = [IsAuthenticatedOrReadOnly]
    pagination_class = paginations.CommentsPagination

    def get_queryset(self):
        return Comment.objects.all().exclude(shown=False)

    def get(self, request, post_id):
        all_comments = self.get_queryset().filter(post__id=post_id)

        if request.user.is_authenticated:
            user_comments = all_comments.filter(user=request.user)
            user_comments.order_by('-date')
            other_users_comments = all_comments.exclude(user=request.user)
            other_users_comments.order_by('-date')
            comments = list(user_comments) + list(other_users_comments)
        else:
            comments = all_comments
        data = PostCommentSerializer(comments, many=True).data
        return Response(data)

    def post(self, request, post_id):
        serializer = self.get_serializer(data=request.data)
        post = Post.objects.all().filter(id=post_id)
        serializer.is_valid(raise_exception=True)
        comment = serializer.save()
        self.set_replies(serializer, comment)
        comment.post = post
        comment.save()
        return Response({"detail": "کامنت شما ثبت شد."})

    @staticmethod
    def set_replies(comment):
        reply_to = comment.reply_to
        if reply_to.replies is '':
            reply_to.replies += str(comment.id)
        else:
            reply_to.replies += (',' + str(comment.id))
