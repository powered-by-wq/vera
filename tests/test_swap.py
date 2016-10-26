from rest_framework.test import APITestCase
from django.conf import settings
import unittest
from rest_framework import status
from vera.models import Site, ReportStatus, Parameter, EventResult
from django.contrib.auth.models import User


class SwapTestCase(APITestCase):

    @unittest.skipUnless(settings.SWAP, "requires swapped models")
    def test_site_swap(self):
        site = Site.objects.find("Site 1")
        site.type = "TYPE1"
        site.save()

        site = Site.objects.find("Site 1")
        self.assertEqual(site.type, "TYPE1")


class SwapRestTestCase(APITestCase):
    def setUp(self):
        if not settings.SWAP:
            return

        Site.objects.find('site-1')
        user = User.objects.create(username='testuser', is_superuser=True)
        self.client.force_authenticate(user=user)

        valid = ReportStatus.objects.find('valid')
        valid.is_valid = True
        valid.save()

        param = Parameter.objects.find('Temperature')
        param.is_numeric = True
        param.units = 'C'
        param.save()

    @unittest.skipUnless(settings.SWAP, "requires swapped models")
    def test_vera_post(self):
        form = {
            'event[site][slug]': 'site-1',
            'event[date]': '2016-12-31',
            'results[0][type_id]': 'temperature',
            'results[0][value]': 6,
            'results[0][flag]': '>',
            'status[slug]': 'valid'
        }
        response = self.client.post('/reports.json', form)
        return
        self.assertEqual(
            response.status_code, status.HTTP_201_CREATED,
            response.data
        )
        self.assertEqual(
            response.data['event_label'],
            "site-1 on 2014-01-03"
        )
        self.assertIn("results", response.data)
        self.assertEqual(len(response.data["results"]), 1)
        event_id = response.data['event_id']

        event = self.client.get('/events/%s.json' % event_id).data
        self.assertEqual(len(event['results']), 1)

        event = self.client.get('/events/%s.json' % event_id).data
        self.assertEqual(len(event['results']), 1)
        result = event['results'][0]
        self.assertEqual(result['value'], 6)
        self.assertEqual(result['flag'], '>')

        er = EventResult.objects.get(event_id=event_id)
        self.assertEqual(er.result_flag, '>')
