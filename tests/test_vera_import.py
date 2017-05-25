from data_wizard.test import WizardTestCase

from vera.models import ReportStatus, Parameter
from vera.models import Site, Event, EventResult
from django.conf import settings


class BaseImportTestCase(WizardTestCase):
    available_apps = (
        'django.contrib.contenttypes',
        'django.contrib.auth',
        'wq.db.patterns.identify',
        'data_wizard',
        'vera.params',
        'vera.series',
        'vera.results',
        'tests.file_app',
    )
    if settings.SWAP:
        available_apps += (
            'tests.swap_app',
        )

    with_wqdb = True
    file_url = '/files.json'
    file_content_type = 'file_app.file'


class BaseReportTestCase(BaseImportTestCase):
    pids = {}

    def setUp(self):
        super(BaseReportTestCase, self).setUp()

        self.site = Site.objects.find("Site #1")
        self.valid = ReportStatus.objects.create(
            is_valid=True,
            slug='valid',
            pk=100,
        )

        parameters = [
            ('Temperature', 'C'),
            ('Notes', None),
        ]
        for name, units in parameters:
            param = Parameter.objects.find(name)
            param.units = units
            if units:
                param.is_numeric = True
            param.save()
            self.pids[name] = param.pk


class ReportTestCase(BaseReportTestCase):
    serializer_name = "vera.series.wizard.ReportSerializer"

    def test_report_import(self):
        # Upload file
        run = self.upload_file('report.csv')

        # Inspect unmatched columns and select choices
        self.check_columns(run, 4, 4)

        rtmpl = 'results[][value];type_id=%s'
        self.update_columns(run, {
            'Report': {
                'site id': 'event[site][slug]',
                'date': 'event[date]',
            },
            'Results': {
                'temperature': rtmpl % self.pids['Temperature'],
                'notes': rtmpl % self.pids['Notes'],
            }
        })

        # Check site identifiers
        self.check_row_identifiers(run, 1, 1)
        site_ctid = 'params.site'
        if settings.SWAP:
            site_ctid = 'swap_app.site'

        self.update_row_identifiers(run, {
            site_ctid: {
                'Site 1': 'site-1',
            }
        })

        # Start data import process, wait for completion
        self.start_import(run, [])

        # Verify results
        self.assert_status(run, 3)
        self.assert_ranges(run, [
            "Data Column 'date -> event[date]' at Rows 1-3, Column 0",
            "Data Column 'site id -> event[site][slug]' at Rows 1-3, Column 1",
            "Data Column 'temperature -> results[][value] (attr=%s)'"
            " at Rows 1-3, Column 2" % self.pids['Temperature'],
            "Data Column 'notes -> results[][value] (attr=%s)'"
            " at Rows 1-3, Column 3" % self.pids['Notes'],
            "Cell value 'Site 1 -> site-1 (event[site][slug])'"
            " at Rows 1-3, Column 1",
        ])
        self.assert_records(run, [
            "imported 'Report for site-1 on 2014-01-05' at row 1",
            "imported 'Report for site-1 on 2014-01-06' at row 2",
            "imported 'Report for site-1 on 2014-01-07' at row 3",
        ])

        # Verify Event status
        for event in Event.objects.all():
            self.assertTrue(event.is_valid)
            self.assertEqual(event.site, self.site)
        self.assertEqual(EventResult.objects.count(), 6)
        param = Parameter.objects.find('temperature')
        er = EventResult.objects.get(
            result_type=param, event_date='2014-01-07'
        )
        self.assertEqual(er.result_value_numeric, 1.0)

        param = Parameter.objects.find('notes')
        er = EventResult.objects.get(
            result_type=param, event_date='2014-01-06'
        )
        self.assertEqual(er.result_value_text, "Test Note 2")


class ReportResultTestCase(BaseReportTestCase):
    serializer_name = 'vera.series.wizard.ReportResultSerializer'

    def test_report_result_import(self):
        # Upload file
        run = self.upload_file('reportresult.csv')

        # Inspect unmatched columns and select choices
        self.check_columns(run, 4, 4)

        self.update_columns(run, {
            'Report': {
                'site id': 'event[site][slug]',
                'date': 'event[date]',
            },
            'Result': {
                'parameter': 'result[type_id]',
                'value': 'result[value]',
            }
        })

        # Check site identifiers
        self.check_row_identifiers(run, 3, 3)
        site_ctid = 'params.site'
        if settings.SWAP:
            site_ctid = 'swap_app.site'

        self.update_row_identifiers(run, {
            site_ctid: {
                'Site 1': 'site-1',
            },
            'params.parameter': {
                'temperature': self.pids['Temperature'],
                'notes': self.pids['Notes'],
            }
        })

        # Start data import process, wait for completion
        self.start_import(run, [])

        # Verify results
        self.assert_status(run, 6)
        self.assert_ranges(run, [
            "Data Column 'date -> event[date]' at Rows 1-6, Column 0",
            "Data Column 'site id -> event[site][slug]' at Rows 1-6, Column 1",
            "Data Column 'parameter -> result[type_id]'"
            " at Rows 1-6, Column 2",
            "Data Column 'value -> result[value]' at Rows 1-6, Column 3",
            "Cell value 'Site 1 -> site-1 (event[site][slug])'"
            " at Rows 1-6, Column 1",
            "Cell value 'temperature -> %s (result[type_id])'"
            " at Rows 1-5, Column 2" % self.pids['Temperature'],
            "Cell value 'notes -> %s (result[type_id])'"
            " at Rows 2-6, Column 2" % self.pids['Notes'],
        ])
        self.assert_records(run, [
            "imported 'Report for site-1 on 2014-01-05' at row 1",
            "imported 'Report for site-1 on 2014-01-05' at row 2",
            "imported 'Report for site-1 on 2014-01-06' at row 3",
            "imported 'Report for site-1 on 2014-01-06' at row 4",
            "imported 'Report for site-1 on 2014-01-07' at row 5",
            "imported 'Report for site-1 on 2014-01-07' at row 6",
        ])

        # Verify Event status
        for event in Event.objects.all():
            self.assertTrue(event.is_valid)
            self.assertEqual(event.site, self.site)
        self.assertEqual(EventResult.objects.count(), 6)
        param = Parameter.objects.find('temperature')
        er = EventResult.objects.get(
            result_type=param, event_date='2014-01-07'
        )
        self.assertEqual(er.result_value_numeric, 1.0)

        param = Parameter.objects.find('notes')
        er = EventResult.objects.get(
            result_type=param, event_date='2014-01-06'
        )
        self.assertEqual(er.result_value_text, "Test Note 2")


class AcisTestCase(BaseImportTestCase):
    def test_acis_import(self):
        # Test ACIS data downloaded from data.rcc-acis.org via climata

        # Configure status
        ReportStatus.objects.create(
            is_valid=True,
            slug='valid',
            pk=100,
        )

        # Import sites
        self.serializer_name = 'vera.params.wizard.SiteSerializer'
        run = self.upload_file(
            'siteswap.csv' if settings.SWAP else 'site.csv'
        )
        self.auto_import(run, expect_input_required=False)

        self.assertEqual(Site.objects.count(), 4)
        msp = Site.objects.find('MSP')
        self.assertEqual(msp.name, 'MINNEAPOLIS/ST PAUL AP')
        if settings.SWAP:
            self.assertEqual(msp.type, 'airport')
        else:
            self.assertEqual(msp.latitude, 44.88305)
            self.assertEqual(msp.longitude, -93.22889)

        # Import parameters
        self.serializer_name = 'vera.params.wizard.ParameterSerializer'
        run = self.upload_file('parameter.csv')
        self.auto_import(run, expect_input_required=False)

        self.assertEqual(Parameter.objects.count(), 4)
        temp = Parameter.objects.find('temperature')
        self.assertEqual(temp.name, 'Temperature')
        self.assertEqual(temp.units, 'F')

        # Upload data file
        self.serializer_name = 'vera.series.wizard.ReportSerializer'
        run = self.upload_file('acis.csv')
        self.auto_import(run, expect_input_required=True)

        # Update columns
        rtmpl = 'results[][value];type_id=%s'
        self.update_columns(run, {
            'Report': {
                'site': 'event[site][slug]',
                'date': 'event[date]',
            },
            'Results': {
                'avgt': rtmpl % Parameter.objects.find('temperature').pk,
                'pcpn': rtmpl % Parameter.objects.find('precipitation').pk,
                'snow': rtmpl % Parameter.objects.find('snowfall').pk,
                'snwd': rtmpl % Parameter.objects.find('snow-depth').pk,
            }
        })
        self.auto_import(run, expect_input_required=True)

        # Update identifiers
        site_ctid = 'params.site'
        if settings.SWAP:
            site_ctid = 'swap_app.site'

        self.update_row_identifiers(run, {
            site_ctid: {
                'MSP': 'MSP',
                'ORD': 'ORD',
                'LAX': 'LAX',
                'JFK': 'JFK',
            }
        })

        self.auto_import(run, expect_input_required=False)

        # Verify Event status
        self.assertEqual(Event.objects.count(), 4 * 31)
        self.assertEqual(
            Event.objects.find('MSP', '2017-01-15').vals['temperature'],
            17.5,
        )
        self.assertEqual(
            Event.objects.find('JFK', '2017-01-15').vals['snow-depth'],
            2.0,
        )

        # Make sure no sites were created on the fly
        self.assertEqual(Site.objects.count(), 4)
