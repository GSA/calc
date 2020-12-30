// @ts-check
import Enzyme from 'enzyme';
import Adapter from 'enzyme-adapter-react-16';
import { populateScheduleLabels } from '../schedule-metadata';

populateScheduleLabels([{
  sin: '899',
  schedule: 'Environmental',
  full_name: '899 - Legacy Environmental',
}, {
  sin: '87405',
  schedule: 'Logistics',
  full_name: '87405 - Legacy Logistics',
}, {
  sin: '874',
  schedule: 'MOBIS',
  full_name: '874 - Legacy MOBIS',
}, {
  sin: '871',
  schedule: 'PES',
  full_name: '871 - Legacy PES',
}, {
  sin: '73802',
  schedule: 'Language Services',
  full_name: '73802 - Legacy Language',
}, {
  sin: '541',
  schedule: 'AIMS',
  full_name: '541 - Legacy AIMS',
}, {
  sin: '520',
  schedule: 'FABS',
  full_name: '520 - Legacy FABS',
}, {
  sin: '132',
  schedule: 'IT Schedule 70',
  full_name: '132 - IT 70',
}, {
  sin: '',
  schedule: 'Consolidated',
  full_name: 'Consolidated'
}]);

Enzyme.configure({ adapter: new Adapter() });
