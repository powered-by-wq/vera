import swapper


Site = swapper.load_model('params', 'Site')
ReportStatus = swapper.load_model('params', 'ReportStatus')
Parameter = swapper.load_model('params', 'Parameter')

Event = swapper.load_model('series', 'Event')
Report = swapper.load_model('series', 'Report')

Result = swapper.load_model('results', 'Result')
EventResult = swapper.load_model('results', 'EventResult')


__all__ = [
   'Site',
   'ReportStatus',
   'Parameter',
   'Event',
   'Report',
   'Result',
   'EventResult',
]
