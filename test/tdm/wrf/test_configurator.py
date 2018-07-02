import unittest
import yaml
from tdm.wrf import configurator


def flatten_flat(assigned):
    f = []
    for k, v in assigned.items():
        if isinstance(v, dict):
            for k1, v1 in flatten_flat(v):
                f.append((k + '.' + k1, v1))
        else:
            f.append((k, v))
    return f


def flatten_global(assigned):
    return flatten_flat(assigned['global'])


def flatten_domains(assigned):
    domains = assigned['domains']
    f = []
    for dn in domains:
        f = f + [('@{}.{}'.format(dn, k), v)
                 for k, v in flatten_flat(domains[dn])]
    return f


class test_configurator(unittest.TestCase):

    def setUp(self):
        with open('minimal.yaml') as f:
            assigned = yaml.load(f.read())
        self.assigned = assigned
        self.c = configurator.make(assigned)

    def check_minimal(self):
        c = self.c
        assigned = self.assigned
        for i, d in enumerate(c.domains_sequence):
            self.assertEqual(i + 1, c.domains[d].id)
        for k, v in flatten_global(assigned):
            self.assertEqual(c[k], v)
        for kd, v in flatten_domains(assigned):
            dn, k = kd[1:].split('.', 1)
            if k.find('parent') == -1:
                self.assertEqual(c.domains[dn][k], v)
        test_vals = {'geogrid.io_form_geogrid': 2,
                     'running.input.restart': False,
                     'physics.ishallow': 0}
        for k, v in test_vals.items():
            self.assertEqual(v, c[k])

    def check_update(self):
        c = self.c
        updates = [('@base.geometry.e_we', 131),
                   ('@dom1.geometry.e_we', 202),
                   ('@dom2.timespan.start.year', 2019),
                   ('@dom2.timespan.start.month', 6),
                   ('geometry.truelat1', 43),
                   ('foobar.foo.bar', 'this is a string')]
        c.update(dict(updates))
        for kd, v in updates:
            if kd.startswith('@'):
                dn, k = kd[1:].split('.', 1)
                if k != 'parent':
                    self.assertEqual(c.domains[dn][k], v)
            else:
                self.assertEqual(c[kd], v)

    def check_generation(self):
        c = self.c
        share = c.generate_share()
        geogrid = c.generate_geogrid()
        ungrib = c.generate_ungrib()
        metgrid = c.generate_metgrid()

    def check_domains(self):
        c = self.c
        for dn, dv in c.domains.items():
            self.assertEqual(dn, dv.name)
        self.assertAlmostEqual(c.domains['base'].get_offset_wrt_base(),
                               (0.0, 0.0))
        self.assertAlmostEqual(c.domains['base'].get_extension(),
                               (1200000, 2400000))
        self.assertAlmostEqual(c.domains['dom1'].get_offset_wrt_base(),
                               (288000.0, 600000.0))
        self.assertAlmostEqual(c.domains['dom1'].get_extension(),
                               (360000.0, 720000.0))


def suite():
    suite_ = unittest.TestSuite()
    suite_.addTest(test_configurator('check_minimal'))
    suite_.addTest(test_configurator('check_update'))
    suite_.addTest(test_configurator('check_generation'))
    suite_.addTest(test_configurator('check_domains'))
    return suite_


if __name__ == '__main__':
    _RUNNER = unittest.TextTestRunner(verbosity=2)
    _RUNNER.run((suite()))
