

try:
    from urllib.parse import urlencode
except ImportError:
    from urllib.parse import urlencode

from django.test import TestCase

from froide.foirequest.tests import factories
from froide.foirequest.models import FoiRequest, FoiAttachment


class ApiTest(TestCase):
    def setUp(self):
        self.site = factories.make_world()

    def test_list(self):
        response = self.client.get('/api/v1/request/?format=json')
        self.assertEqual(response.status_code, 200)
        response = self.client.get('/api/v1/message/?format=json')
        self.assertEqual(response.status_code, 200)
        response = self.client.get('/api/v1/attachment/?format=json')
        self.assertEqual(response.status_code, 200)

    def test_detail(self):
        req = FoiRequest.objects.all()[0]
        response = self.client.get('/api/v1/request/%d/?format=json' % req.pk)
        self.assertEqual(response.status_code, 200)
        self.assertIn(req.title, response.content.decode('utf-8'))
        self.assertNotIn(req.secret_address, response.content.decode('utf-8'))
        req.user.private = True
        req.user.save()

        mes = factories.FoiMessageFactory.create(
            request=req,
            subject=req.user.get_full_name(),
            plaintext='Hallo %s,\n%s\n%s' % (
                req.user.get_full_name(),
                req.secret_address,
                req.user.address
            )
        )
        response = self.client.get('/api/v1/message/%d/?format=json' % mes.pk)
        self.assertEqual(response.status_code, 200)
        self.assertNotIn(req.user.get_full_name(), response.content.decode('utf-8'))
        self.assertNotIn(req.secret_address, response.content.decode('utf-8'))
        self.assertNotIn(req.user.address, response.content.decode('utf-8'))

        att = FoiAttachment.objects.all()[0]
        att.approved = True
        att.save()
        response = self.client.get('/api/v1/attachment/%d/?format=json' % att.pk)
        self.assertEqual(response.status_code, 200)

    def test_permissions(self):
        req = factories.FoiRequestFactory.create(
            visibility=1, site=self.site)

        response = self.client.get('/api/v1/request/%d/?format=json' % req.pk)
        self.assertEqual(response.status_code, 404)

        mes = factories.FoiMessageFactory.create(request=req)
        response = self.client.get('/api/v1/message/%d/?format=json' % mes.pk)
        self.assertEqual(response.status_code, 404)

        att = factories.FoiAttachmentFactory.create(belongs_to=mes)
        att.approved = True
        att.save()
        response = self.client.get('/api/v1/attachment/%d/?format=json' % att.pk)
        self.assertEqual(response.status_code, 404)

    def test_content_hidden(self):
        marker = 'TESTMARKER'
        mes = factories.FoiMessageFactory.create(
            content_hidden=True,
            plaintext=marker
        )
        response = self.client.get('/api/v1/message/%d/?format=json' % mes.pk)
        self.assertEqual(response.status_code, 200)
        self.assertNotIn(marker, response.content.decode('utf-8'))

    def test_username_hidden(self):
        user = factories.UserFactory.create(
            first_name='Reinhardt'
        )
        user.private = True
        user.save()
        mes = factories.FoiMessageFactory.create(
            content_hidden=True,
            sender_user=user
        )
        response = self.client.get('/api/v1/message/%d/?format=json' % mes.pk)
        self.assertEqual(response.status_code, 200)
        self.assertNotIn(user.username, response.content.decode('utf-8'))
        self.assertNotIn(user.first_name, response.content.decode('utf-8'))

    def test_search(self):
        response = self.client.get('/api/v1/request/search/?format=json&q=Number')
        self.assertEqual(response.status_code, 200)

    def test_search_similar(self):
        simple_search_url = '/api/v1/request/simplesearch/?format=json'
        response = self.client.get(simple_search_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual('{"objects": []}', response.content.decode('utf-8'))
        self.assertEqual(response['Content-Type'], 'application/json')
        req = FoiRequest.objects.all()[0]
        factories.rebuild_index()
        response = self.client.get('%s&%s' % (
            simple_search_url, urlencode({'q': req.title})
        ))
        self.assertEqual(response.status_code, 200)
        content = response.content.decode('utf-8')
        self.assertIn('title', content)
        self.assertIn('description', content)
        self.assertIn('public_body_name', content)
        self.assertIn('url', content)
