from django.utils import timezone
from django.core.paginator import Paginator


def filter_published_posts(posts, show_all_for_author=None):
    current_datetime = timezone.now()
    
    if show_all_for_author:
        return posts
    else:
        return posts.filter(
            is_published=True,
            category__is_published=True,
            pub_date__lte=current_datetime
        )


def paginate_queryset(request, queryset, per_page=10):
    paginator = Paginator(queryset, per_page)
    page_number = request.GET.get('page')
    return paginator.get_page(page_number)