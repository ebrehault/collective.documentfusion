from zope.interface import implements, Interface
from zope.component import getUtility, adapts
from zope.schema import getFieldsInOrder

from Products.Five.browser import BrowserView
from plone.dexterity.interfaces import IDexterityFTI, IDexterityContent
from collective.documentfusion.interfaces import ISourceFile, IFusionData
from plone.namedfile.interfaces import INamedField
from zope.schema._schema import getFieldNames


class DexterityFusionData(object):
    adapts(IDexterityContent, Interface)
    implements(IFusionData)

    def __init__(self, context, request):
        self.context = context

    def __call__(self):

        context = self.context
        data = {}
        data['id'] = context.id
        data['url'] = context.absolute_url()
        data['path'] = '/'.join(context.getPhysicalPath())
        data['uid'] = context.UID()
        fti = getUtility(IDexterityFTI, name=context.portal_type)
        schema = fti.lookupSchema()
        for name in getFieldNames(schema):
            data[name] = getattr(context, name, None)

        return data


class DexteritySourceFile(BrowserView):
    adapts(IDexterityContent, Interface)
    implements(ISourceFile)

    def __init__(self, context, request):
        self.context = context

    def __call__(self):
        fti = getUtility(IDexterityFTI, name=self.context.portal_type)
        schema = fti.lookupSchema()
        for name, field in getFieldsInOrder(schema):
            if INamedField.providedBy(field):
                return getattr(self.context, name)
        else:
            return None