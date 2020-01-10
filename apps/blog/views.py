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
    serializer_class = CommentSerializer
    queryset = Comment.objects.all().order_by('-date')
    permission_classes = [IsAuthenticatedOrReadOnly]
    pagination_class = paginations.CommentsPagination

    def get_queryset(self):
        return Comment.objects.all().exclude(shown=False)

    def get(self, request, post_id):
        father_comments = self.get_queryset().filter(post_id=post_id).filter(reply_to=None)
        comments = []
        for comment in father_comments:
            reply_comments = []
            for reply_comment_id in eval(comment.replies):
                reply_comments.append(self.get_queryset().get(id=reply_comment_id))
            reply_comments.sort(key=lambda x: x.date)
            comments.append(comment)
            comments.extend(reply_comments)

        data = CommentSerializer(comments, many=True).data
        return Response(data)

    def post(self, request, post_id):
        serializer = self.get_serializer(data=request.data)
        post = Post.objects.all().filter(id=post_id)
        serializer.is_valid(raise_exception=True)
        comment = serializer.save()
        self.set_replies(comment)
        comment.post = post
        comment.save()
        return Response({"detail": "کامنت شما ثبت شد."})

    @staticmethod
    def set_replies(comment):
        reply_to = comment.reply_to
        replies = eval(reply_to.replies)
        replies.append(comment.id)
