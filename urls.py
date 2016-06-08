



from django.views.decorators.cache import cache_page
from django.conf.urls import *
import zunzun.views
import settings

urlpatterns = patterns('',
    (r"^$", zunzun.views.HomePageView),
    
    (r"^StatusAndResults/", zunzun.views.StatusView),
    
    (r"^CharacterizeData/([123])/$", zunzun.views.LongRunningProcessView),
    (r"^StatisticalDistributions/([1])/$", zunzun.views.LongRunningProcessView),    
    (r"^FunctionFinder__1___/([23])/$", zunzun.views.LongRunningProcessView),
    (r"^FunctionFinderResults/([23])/$", zunzun.views.LongRunningProcessView),
    (r"^FitEquation__1___/([23])/(.+)/(.+)/$", zunzun.views.LongRunningProcessView),
    (r"^Equation/([23])/(.+)/(.+)/$", zunzun.views.LongRunningProcessView),
    
    (r"^EvaluateAtAPoint/$", zunzun.views.EvaluateAtAPointView),

    (r"^AllEquations/([23])/(.+)/$", zunzun.views.AllEquationsView),
    (r"^Feedback/$", zunzun.views.FeedbackView),
)
