from zope.interface import implements, Interface
from zope.component import getUtility, adapts, getMultiAdapter
from zope.schema import getFieldsInOrder, getFieldNames

from Products.CMFPlone.utils import base_hasattr
from plone import api
from plone.app.relationfield.behavior import IRelatedItems
from plone.dexterity.interfaces import IDexterityFTI, IDexterityContent
from plone.namedfile.interfaces import INamedField

from collective.documentfusion.interfaces import ISourceFile, IFusionData,\
    IMergeDataSources


class DexterityFusionData(object):
    adapts(IDexterityContent, Interface)
    implements(IFusionData)

    def __init__(self, context, request):
        self.context = context

    def __call__(self):

        context = self.context
        data = {}
        data['document_id'] = context.id
        data['url'] = context.absolute_url()
        data['path'] = '/'.join(context.getPhysicalPath())
        data['uid'] = context.UID()
        if base_hasattr(context, 'title') and context.title:
            data['Title'] = context.title

        if base_hasattr(context, 'creators'):
            creator = context.creators[0]
            user = api.user.get(creator)
            if user:
                data['Author'] = user.getProperty('fullname', '') or creator
            else:
                data['Author'] = creator

        if base_hasattr(context, 'description') and context.description:
            description = context.description.replace('\n', ' ').strip()
            if description:
                data['Subject'] = data['Description'] = description

        if base_hasattr(context, 'subject') and context.subject:
            keywords = tuple([k.strip() for k in context.subject if k.strip()])
            data['Keywords'] = keywords

        fti = getUtility(IDexterityFTI, name=context.portal_type)
        schema = fti.lookupSchema()
        for name in getFieldNames(schema):
            data[name] = getattr(context, name, None)

        return data


class DexteritySourceFile(object):
    adapts(IDexterityContent, Interface)
    implements(ISourceFile)

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self, recursive=True):
        # look for a content with name file field into content
        fti = getUtility(IDexterityFTI, name=self.context.portal_type)
        schema = fti.lookupSchema()
        for name, field in getFieldsInOrder(schema):
            if INamedField.providedBy(field):
                return getattr(self.context, name)

        # else, look for a source file field into related items
        if recursive and IRelatedItems.providedBy(self.context):
            related_items = [r.to_object for r in self.context.relatedItems]
            for related_item in related_items:

                source_file = getMultiAdapter((related_item, self.request),
                                              ISourceFile
                                              )()
                if source_file:
                    return source_file
                else:
                    continue

        return None


class DexterityMergeDataSources(object):
    adapts(IDexterityContent, Interface)
    implements(IMergeDataSources)

    def __init__(self, context, request):
        self.context = context

    def __call__(self):
        if IRelatedItems.providedBy(self.context):
            return [r.to_object for r in self.context.relatedItems if r]
        else:
            return []