import unittest
import yaml
from tdm.wrf import configurator

def flatten_flat(assigned):
    f = []
    for k, v in assigned.items():
        if k != 'domains':
            if isinstance(v, dict):
                for k1, v1 in flatten_flat(v):
                    f.append((k + '.' + k1, v1))
            else:
                f.append((k, v))
    return f

def flatten_domains(path, assigned):
    f = []
    for k, v in assigned.items():
        if k == 'domains':
            for dn in v:
                for k1, v1 in flatten_flat(v[dn]):
                    f.append(('@{}.'.format(dn) + path + '.' + k1, v1))
        elif isinstance(v, dict):
            f = f + flatten_domains(path + '.' + k if path else k, v)
    return f
    
class test_configurator(unittest.TestCase):


    def check_minimal(self):
        with open('minimal.yaml') as f:
            assigned = yaml.load(f.read())
        c = configurator.make(assigned)
        for k, v in flatten_flat(assigned):
            self.assertEqual(c.conf[k], v)
        for kd, v in flatten_domains('', assigned):
            dn, k = kd[1:].split('.', 1)
            if k.find('parent') == -1:
                self.assertEqual(c.domains[dn][k], v)
        
def suite():
    suite_ = unittest.TestSuite()
    suite_.addTest(test_configurator('check_minimal'))
    return suite_

if __name__ == '__main__':
    _RUNNER = unittest.TextTestRunner(verbosity=2)
    _RUNNER.run((suite()))
