from django.views.decorators.cache import cache_page
from django.conf.urls import *
import zunzun.views
import settings

try: # newer versions of django
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
except: # older versions of django
    urlpatterns = [
        url(r"^$", zunzun.views.HomePageView),
        url(r"^StatusAndResults/", zunzun.views.StatusView),
        url(r"^CharacterizeData/([123])/$", zunzun.views.LongRunningProcessView),
        url(r"^StatisticalDistributions/([1])/$", zunzun.views.LongRunningProcessView),    
        url(r"^FunctionFinder__1___/([23])/$", zunzun.views.LongRunningProcessView),
        url(r"^FunctionFinderResults/([23])/$", zunzun.views.LongRunningProcessView),
        url(r"^FitEquation__1___/([23])/(.+)/(.+)/$", zunzun.views.LongRunningProcessView),
        url(r"^Equation/([23])/(.+)/(.+)/$", zunzun.views.LongRunningProcessView),
        url(r"^EvaluateAtAPoint/$", zunzun.views.EvaluateAtAPointView),
        url(r"^AllEquations/([23])/(.+)/$", zunzun.views.AllEquationsView),
        url(r"^Feedback/$", zunzun.views.FeedbackView),
]   
