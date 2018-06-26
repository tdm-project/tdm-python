# import yaml

from datetime import datetime
from .constants import DEFAULTS


def merge_configs(base, update):
    assert type(base) == type(update)
    if not isinstance(base, dict):
        return update
    res = {}
    for k in base:
        if k not in update:
            res[k] = base[k]
    for k in update:
        if k not in base:
            res[k] = update[k]
        else:
            res[k] = merge_configs(base[k], update[k])
    return res


class confbox(dict):
    @staticmethod
    def subconfbox(conf):
        for k in conf:
            if isinstance(conf[k], dict):
                conf[k] = confbox(conf[k])

    @staticmethod
    def build_date(cbox):
        now = datetime.utcnow()
        date = datetime(cbox.get('year', now.year),
                        cbox.get('month', now.month),
                        cbox.get('day', now.day),
                        cbox.get('hour', now.hour),
                        cbox.get('minute', now.minute),
                        cbox.get('second', now.second))
        return date.strftime("%Y-%m-%d_%H:%M:%S")

    def __init__(self, conf):
        super(confbox, self).__init__()
        for k, v in conf.items():
            self[k] = confbox(v) if isinstance(v, dict) else v

    def __getitem__(self, k):
        def get_deep(c, p):
            if len(p) == 1:
                return c.getattr_base(p[0])
            if p[0] in c:
                return get_deep(c[p[0]], p[1:])
            else:
                raise KeyError(p[0])
        return get_deep(self, k.split('.'))

    def getattr_base(self, k):
        if k in self:
            return super(confbox, self).__getitem__(k)
        if k == 'start_date' and 'start' in self:
            return self.build_date(self['start'])
        if k == 'end_date' and 'end' in self:
            return self.build_date(self['end'])
        raise KeyError(k)


class domain(confbox):
    def __init__(self, conf):
        super(domain, self).__init__(conf)
        self.parent = None

    def __getitem__(self, k):
        try:
            return super(domain, self).__getitem__(k)
        except KeyError as e:
            if self.parent is None:
                raise KeyError(e)
            return self.parent[k]

    def set_parent(self, ds):
        if 'parent' in self['geometry']:
            self.parent = ds[self['geometry.parent']]


class configurator(object):
    @staticmethod
    def remove_domain_info(conf):
        if not isinstance(conf, dict):
            return conf
        return dict((k, configurator.remove_domain_info(conf[k]))
                    for k in conf if k != 'domains')

    @staticmethod
    def gather_domains_info(conf):
        ds = {}

        def wrap(p, o):
            return o if not p else {p[0]: wrap(p[1:], o)}

        def absorbe(path, conf):
            for k in conf:
                ds.setdefault(k, {})[path[0]] = wrap(path[1:], conf[k])

        def helper(path, conf):
            path = list() if path is None else path
            for k in conf:
                if k == 'domains':
                    absorbe(path, conf[k])
                else:
                    if isinstance(conf[k], dict):
                        helper(path + [k], conf[k])

        helper(None, conf)
        for n in ds:
            ds[n] = domain(ds[n])
        for n in ds:
            ds[n].set_parent(ds)
        return ds

    @classmethod
    def make(cls, assigned=None):
        return cls(merge_configs(
            DEFAULTS, {} if assigned is None else assigned))

    def __init__(self, conf):
        self.conf = confbox(self.remove_domain_info(conf))
        self.domains = self.gather_domains_info(conf)
        self.domains_sequence = ['base'] + sorted(_ for _ in self.domains
                                                  if _ != 'base')

    def gather_data(self, tags):
        def helper(t):
            if t == 'domains.max_dom':
                return ('max_dom', len(self.domains))
            p = t.split('.')
            if p[0] == 'domains':
                t = '.'.join(p[1:])
                v = [self.domains[n][t]
                     for n in self.domains_sequence]
            else:
                v = self.conf[t]
            return (p[-1], v)
        return dict(helper(_) for _ in tags)

    def generate_section(self, sname, fields):

        def format_value(v):
            if isinstance(v, list):
                return ', '.join(map(format_value, v))
            elif isinstance(v, (int, float)):
                return '{}'.format(v)
            elif isinstance(v, bool):
                return '.true.' if v else '.false.'
            else:
                return "'{}'".format(v)
        body = ',\n '.join('{} = {}'.format(fn, format_value(fields[fn]))
                           for fn in fields)

        return '&{}\n {}\n/\n'.format(sname, body)

    def generate_share(self):
        fields = self.gather_data([
            'dynamics.wrf_core', 'domains.max_dom',
            'domains.timespans.start_date',
            'domains.timespans.end_date',
            'running.input.interval_seconds',
            'conversions.geogrid.io_form_geogrid'
            ])
        return self.generate_section('share', fields)


    def generate_physics(self):
        pass
    def generate_time_control(self):
        pass
    def generate_domains(self):
        pass
    def generate_dynamics(self):
        pass
    def generate_boundary_control(self):
        pass
    def generate_namelist_quilt(self):
        fields = self.gather_data(['nio_tasks_per_group', 'nio_groups'])
        return self.generate_section('namelist_quilt', fields)
    def generate_fdda(self):
        return self.generate_section('fdda', {})
    def generate_grib2(self):
        return self.generate_section('grib2', {})
    def generate_wsp_namelist(self, fname='namelist.wsp'):
        pass

