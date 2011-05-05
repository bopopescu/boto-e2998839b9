# Copyright (c) 2010 Reza Lotun http://reza.lotun.name
#
# Permission is hereby granted, free of charge, to any person obtaining a
# copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish, dis-
# tribute, sublicense, and/or sell copies of the Software, and to permit
# persons to whom the Software is furnished to do so, subject to the fol-
# lowing conditions:
#
# The above copyright notice and this permission notice shall be included
# in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
# OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABIL-
# ITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT
# SHALL THE AUTHOR BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
# WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
# IN THE SOFTWARE.
#

from datetime import datetime
from boto.resultset import ResultSet
from boto.ec2.cloudwatch.listelement import ListElement
try:
    import json
except ImportError:
    import simplejson as json


class MetricAlarm(object):

    OK = 'OK'
    ALARM = 'ALARM'
    INSUFFICIENT_DATA = 'INSUFFICIENT_DATA'

    _cmp_map = {
                    '>='    :   'GreaterThanOrEqualToThreshold',
                    '>'     :   'GreaterThanThreshold',
                    '<'     :   'LessThanThreshold',
                    '<='    :   'LessThanOrEqualToThreshold',
               }
    _rev_cmp_map = dict((v, k) for (k, v) in _cmp_map.iteritems())

    def __init__(self, connection=None, name=None, metric=None,
                 namespace=None, statistic=None, comparison=None, threshold=None,
                 period=None, evaluation_periods=None, actions_enabled=None, alarm_action=None,
                 dimensions=None):
        """
        Creates a new Alarm.

        :type name: str
        :param name: Name of alarm.

        :type metric: str
        :param metric: Name of alarm's associated metric.

        :type namespace: str
        :param namespace: The namespace for the alarm's metric.

        :type statistic: str
        :param statistic: The statistic to apply to the alarm's associated
                          metric.
                          Valid values: SampleCount|Average|Sum|Minimum|Maximum

        :type comparison: str
        :param comparison: Comparison used to compare statistic with threshold.
                           Valid values: >= | > | < | <=

        :type threshold: float
        :param threshold: The value against which the specified statistic
                          is compared.

        :type period: int
        :param period: The period in seconds over which teh specified
                       statistic is applied.

        :type evaluation_periods: int
        :param evaluation_period: The number of periods over which data is
                                  compared to the specified threshold.

        :type unit: str
        :param unit: Allowed Values are:
                     Seconds|Microseconds|Milliseconds,
                     Bytes|Kilobytes|Megabytes|Gigabytes|Terabytes,
                     Bits|Kilobits|Megabits|Gigabits|Terabits,
                     Percent|Count|
                     Bytes/Second|Kilobytes/Second|Megabytes/Second|
                     Gigabytes/Second|Terabytes/Second,
                     Bits/Second|Kilobits/Second|Megabits/Second,
                     Gigabits/Second|Terabits/Second|Count/Second|None

        :type description: str
        :param description: Description of MetricAlarm

        :type dimensions: list of dicts
        :param description: Dimensions of alarm, such as:
                            [{'InstanceId':['i-0123456,i-0123457']}]
        
        :type alarm_actions: list of strs
        :param alarm_actions: A list of the ARNs of the actions to take in
                              ALARM state
        
        :type insufficient_data_actions: list of strs
        :param insufficient_data_actions: A list of the ARNs of the actions to
                                          take in INSUFFICIENT_DATA state
        
        :type ok_actions: list of strs
        :param ok_actions: A list of the ARNs of the actions to take in OK state
        """
        self.name = name
        self.connection = connection
        self.metric = metric
        self.namespace = namespace
        self.statistic = statistic
        if threshold is not None:
            self.threshold = float(threshold)
        else:
            self.threshold = None
        self.comparison = self._cmp_map.get(comparison)
        self.period = int(period) if period is not None else None
        self.evaluation_periods = int(evaluation_periods) if evaluation_periods is not None else None
        self.actions_enabled = int(1) if actions_enabled is True else int(0) 
        self.alarm_arn = None
        self.last_updated = None
        self.description = ''
        self.dimensions = dimensions
        self.insufficient_data_actions = []
        self.ok_actions = []
        self.state_reason = None
        self.state_value = None
        self.unit = None
        self.alarm_actions = ListElement(alarm_action) if alarm_action is not None else None

    def __repr__(self):
        return 'MetricAlarm:%s[%s(%s) %s %s]' % (self.name, self.metric,
                                                 self.statistic,
                                                 self.comparison,
                                                 self.threshold)

    def startElement(self, name, attrs, connection):
        if name == 'AlarmActions':
            self.alarm_actions = ListElement()
            return self.alarm_actions
        elif name == 'InsufficientDataActions':
            self.insufficient_data_actions = ListElement()
            return self.insufficient_data_actions
        elif name == 'OKActions':
            self.ok_actions = ListElement()
            return self.ok_actions
        else:
            pass

    def endElement(self, name, value, connection):
        if name == 'ActionsEnabled':
            self.actions_enabled = value
        elif name == 'AlarmArn':
            self.alarm_arn = value
        elif name == 'AlarmConfigurationUpdatedTimestamp':
            self.last_updated = value
        elif name == 'AlarmDescription':
            self.description = value
        elif name == 'AlarmName':
            self.name = value
        elif name == 'ComparisonOperator':
            setattr(self, 'comparison', self._rev_cmp_map[value])
        elif name == 'EvaluationPeriods':
            self.evaluation_periods = int(value)
        elif name == 'MetricName':
            self.metric = value
        elif name == 'Namespace':
            self.namespace = value
        elif name == 'Period':
            self.period = int(value)
        elif name == 'StateReason':
            self.state_reason = value
        elif name == 'StateValue':
            self.state_value = value
        elif name == 'Statistic':
            self.statistic = value
        elif name == 'Threshold':
            self.threshold = float(value)
        elif name == 'Unit':
            self.unit = value
        else:
            setattr(self, name, value)

    def set_state(self, value, reason, data=None):
        """ Temporarily sets the state of an alarm.

        :type value: str
        :param value: OK | ALARM | INSUFFICIENT_DATA

        :type reason: str
        :param reason: Reason alarm set (human readable).

        :type data: str
        :param data: Reason data (will be jsonified).
        """
        return self.connection.set_alarm_state(self.name, reason, value, data)

    def update(self):
        return self.connection.update_alarm(self)

    def enable_actions(self):
        return self.connection.enable_alarm_actions([self.name])

    def disable_actions(self):
        return self.connection.disable_alarm_actions([self.name])

    def describe_history(self, start_date=None, end_date=None, max_records=None,
                         history_item_type=None, next_token=None):
        return self.connection.describe_alarm_history(self.name, start_date,
                                                      end_date, max_records,
                                                      history_item_type,
                                                      next_token)

    def add_alarm_action(self, action_arn=None):
        """
        Adds an alarm action, represented as an SNS topic, to this alarm. 
        What do do when alarm is triggered.

        :type action_arn: str
        :param action_arn: SNS topics to which notification should be 
                           sent if the alarm goes to state ALARM.
        """
        if not action_arn:
            return # Raise exception instead?
        self.actions_enabled = 'true'
        self.alarm_actions.append(action_arn)

    def add_insufficient_data_action(self, action_arn=None):
        """
        Adds an insufficient_data action, represented as an SNS topic, to
        this alarm. What to do when the insufficient_data state is reached.

        :type action_arn: str
        :param action_arn: SNS topics to which notification should be 
                           sent if the alarm goes to state INSUFFICIENT_DATA.
        """
        if not action_arn:
            return
        self.actions_enabled = 'true'
        self.insufficient_data_actions.append(action_arn)
    
    def add_ok_action(self, action_arn=None):
        """
        Adds an ok action, represented as an SNS topic, to this alarm. What
        to do when the ok state is reached.

        :type action_arn: str
        :param action_arn: SNS topics to which notification should be 
                           sent if the alarm goes to state INSUFFICIENT_DATA.
        """
        if not action_arn:
            return
        self.actions_enabled = 'true'
        self.ok_actions.append(action_arn)

    def delete(self):
        self.connection.delete_alarms([self])

class AlarmHistoryItem(object):
    def __init__(self, connection=None):
        self.connection = connection

    def __repr__(self):
        return 'AlarmHistory:%s[%s at %s]' % (self.name, self.summary, self.timestamp)

    def startElement(self, name, attrs, connection):
        pass

    def endElement(self, name, value, connection):
        if name == 'AlarmName':
            self.name = value
        elif name == 'HistoryData':
            self.data = json.loads(value)
        elif name == 'HistoryItemType':
            self.tem_type = value
        elif name == 'HistorySummary':
            self.summary = value
        elif name == 'Timestamp':
            self.timestamp = datetime.strptime(value, '%Y-%m-%dT%H:%M:%S.%fZ')

