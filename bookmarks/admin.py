from django.contrib import admin

from bookmarks import models

class BookmarkAdmin(admin.ModelAdmin):
    list_display = ('content_object', 'key', 'user', 
        'created_at', 'modified_at')
    list_filter = ('content_type', 'created_at', 'modified_at')
    ordering = ('-modified_at',)
    search_fields = ('user', 'key')
    readonly_fields = ('user',)

admin.site.register(models.Bookmark, BookmarkAdmin)
