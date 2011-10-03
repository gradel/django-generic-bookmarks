from django.db.models import get_model
from django import http

from bookmarks import handlers, signals

ERRORS = {
    'model': u'Invalid model.',
    'handler': u'Unregistered model.',
    'key': u'Invalid key.',
}

def bookmark(request):
    if request.method == 'POST':
        
        # getting handler
        model_name = request.POST.get('model')
        model = get_model(*model_name.split('.'))
        if model is None:
            # invalid model -> bad request
            return http.HttpResponseBadRequest(ERRORS['model'])
        handler = handlers.library.get_handler(model)
        if handler is None:
            # bad or unregistered model -> bad request
            return http.HttpResponseBadRequest(ERRORS['handler'])

        # getting form
        form = handler.get_form(request, data=request.POST)
        if form.is_valid():
            instance = form.instance()
            bookmark_model = handler.backend.get_model()

            # validating the bookmark key
            key = handler.get_key(request, instance, form.cleaned_data['key'])
            if not handler.allow_key(request, instance, key):
                return http.HttpResponseBadRequest(ERRORS['key'])
                                
            # pre-save signal: receivers can stop the bookmark process
            # note: one receiver is always called: *handler.pre_save*
            # handler can disallow the vote
            responses = signals.bookmark_pre_save.send(sender=bookmark_model, 
                form=form, request=request)
    
            # if one of the receivers returns False then bookmark process 
            # must be killed
            for receiver, response in responses:
                if response == False:
                    return http.HttpResponseBadRequest(
                        'Receiver %r killed the bookmark process' % 
                        receiver.__name__)
            
            # adding or removing the bookmark
            bookmark = handler.save(request, form)
            created = bool(bookmark)
        
            # post-save signal
            # note: one receiver is always called: *handler.post_save*
            signals.bookmark_post_save.send(sender=bookmark_model, 
                bookmark=bookmark, request=request, created=created)
    
            # process completed successfully: redirect
            return handler.response(request, bookmark, created)
        
        # form is not valid: must handle errors
        return handler.fail(request, form.errors)
        
    # only answer POST requests
    return http.HttpResponseForbidden('Forbidden.')


def ajax_form(request):
    # TODO
    pass