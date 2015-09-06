from rest_framework.test import APITestCase
from rest_pandas.test import parse_csv
from django.conf import settings
import unittest
try:
    from matplotlib.cbook import boxplot_stats
except ImportError:
    boxplot_stats = None

import swapper
Report = swapper.load_model('vera', 'Report')
ReportStatus = swapper.load_model('vera', 'ReportStatus')
Parameter = swapper.load_model('vera', 'Parameter')


class SwapTestCase(APITestCase):
    def setUp(self):
        data = (
            ('2014-01-01', 'Site1', 'Temp', 0.5),
            ('2014-01-02', 'Site1', 'Temp', 0.4),
            ('2014-01-03', 'Site1', 'Temp', 0.6),
            ('2014-01-04', 'Site1', 'Temp', 0.2),
            ('2014-01-05', 'Site1', 'Temp', 0.1),

            ('2014-01-01', 'Site2', 'Temp', 0.4),
            ('2014-01-02', 'Site2', 'Temp', 0.3),
            ('2014-01-03', 'Site2', 'Temp', 0.6),
            ('2014-01-04', 'Site2', 'Temp', 0.7),
            ('2014-01-05', 'Site2', 'Temp', 0.2),

            ('2014-01-01', 'Site2', 'Snow', 0.1),
            ('2014-01-02', 'Site2', 'Snow', 0.0),
            ('2014-01-03', 'Site2', 'Snow', 0.3),
            ('2014-01-04', 'Site2', 'Snow', 0.0),
            ('2014-01-05', 'Site2', 'Snow', 0.0),
        )

        for param in 'Temp', 'Snow':
            p = Parameter.objects.find(param)
            p.is_numeric = True
            p.save()

        valid = ReportStatus.objects.create(pk=1, is_valid=True)
        for date, site, param, value in data:
            Report.objects.create_report(
                (site, date),
                {param: value},
                status=valid
            )

    @unittest.skipUnless(settings.SWAP, "requires swapped models")
    def test_timeseries(self):
        response = self.client.get("/chart/site1/site2/temp/timeseries.csv")
        datasets = self.parse_csv(response)
        self.assertEqual(len(datasets), 2)
        for dataset in datasets:
            self.assertEqual(dataset['parameter'], 'temp')
            self.assertEqual(dataset['units'], '-')
            self.assertEqual(len(dataset['data']), 5)

        if datasets[0]['site'] == "site1":
            s1data = datasets[0]
        else:
            s1data = datasets[1]

        self.assertEqual(s1data['site'], "site1")
        d0 = s1data['data'][0]
        self.assertEqual(d0['date'], '2014-01-01')
        self.assertEqual(d0['value'], 0.5)

    @unittest.skipUnless(settings.SWAP, "requires swapped models")
    def test_scatter(self):
        response = self.client.get("/chart/site2/temp/snow/scatter.csv")

        datasets = self.parse_csv(response)
        self.assertEqual(len(datasets), 1)

        dataset = datasets[0]
        self.assertEqual(dataset['site'], 'site2')
        self.assertEqual(len(dataset['data']), 5)

        d4 = dataset['data'][4]
        self.assertEqual(d4['date'], '2014-01-05')
        self.assertEqual(d4['temp-value'], 0.2)
        self.assertEqual(d4['snow-value'], 0.0)

    @unittest.skipUnless(
        settings.SWAP and boxplot_stats,
        "requires swapped models and matplotlib 1.4+"
    )
    def test_boxplot(self):
        response = self.client.get("/chart/site1/temp/boxplot.csv")

        datasets = self.parse_csv(response)
        self.assertEqual(len(datasets), 1)

        dataset = datasets[0]
        self.assertEqual(dataset['site'], 'site1')
        self.assertEqual(len(dataset['data']), 1)

        stats = dataset['data'][0]
        self.assertEqual(stats['year'], '2014')
        self.assertEqual(stats['value-whislo'], 0.1)
        self.assertEqual(stats['value-mean'], 0.36)
        self.assertEqual(stats['value-whishi'], 0.6)

    def parse_csv(self, response):
        return parse_csv(response.content.decode('utf-8'))
