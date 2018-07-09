import scipy as sp

class Config(tuple):

    def __new__(cls, *args, **kwargs):
        return super().__new__(cls, *args, **kwargs)

    # Convenience properties.

    @property
    def messages(self):
        return [self[idx][1] for idx in cmdidx(self, 'messages')]

    @property
    def box(self):
        return [self[idx][1:] for idx in cmdidx(self, 'box')]

    @property
    def bounds(self):
        return [self[idx][1] for idx in cmdidx(self, 'read_cell_boundary')]

    @property
    def config(self):
        return [self[idx][1] for idx in cmdidx(self, 'config')]
    
    @property
    def input(self):
        return [self[idx][1] for idx in cmdidx(self, 'input')]

    @property
    def dump(self):
        return [self[idx][1] for idx in cmdidx(self, 'dump')]

    @property
    def dump_opts(self):
        idxs = cmdidx(self, 'dump')
        return [dict(self[idx][2]) for idx in idxs]
        
    @property
    def pair_potential(self):
        idxs = cmdidx(self, 'pair_potential')
        keys = [self[idx][1] for idx in idxs]
        values = [dict(self[idx][2]) for idx in idxs]
        return dict((key, val) for key, val in zip(keys, values))



def cmdidx(cfg: Config, cmd_name: str) -> sp.ndarray:
    """ Find index (or indices) of command name. """
    return [idx for idx, cmd in enumerate(cfg) if cmd[0] == cmd_name]


def insert_cmd(cfg: Config, cmd: tuple, where: int) -> Config:
    """ Insert a command into config. """
    return Config(cfg[:where] + (cmd,) + cfg[where:])


def set_cmd_arg(cfg: Config, cmd, opt) -> Config:
    """ Set argument of simple command. """
    idx = [cmd for cmd in cmdidx(cfg, cmd)][0]
    cmd = (cmd, opt)
    return Config(cfg[:idx] + (cmd,) + cfg[idx+1:])


def set_cmd_opt(cfg: Config, *cmds, **opts) -> Config:
    """ Set command options. """
    if len(cmds) == 1:
        idx = [cmd for cmd in cmdidx(cfg, cmds[0])][0]
        _opts = {**cfg[idx][-1], **opts}
        cmd = (cmds[0], _opts)
    elif len(cmds) == 2:
        idx = [cmd for cmd in cmdidx(cfg, cmds[0]) if cfg[cmd][1] == cmds[1]][0]
        _opts = {**cfg[idx][-1], **opts}
        cmd = (cmds[0], cmds[1], _opts)
    return Config(cfg[:idx] + (cmd,) + cfg[idx+1:])


# def set_pair_potential_opt(cfg: Config, potential: str, **opts) -> Config:
#     """ Set pair_potential options for some potential. """
#     idx = [cmd for cmd in cmdidx(cfg, 'pair_potential') if cfg[cmd][1] == potential][0]
#     _opts = {**cfg[idx][-1], **opts}
#     cmd = ('pair_potential', potential, _opts)
#     return Config(cfg[:idx] + (cmd,) + cfg[idx+1:])


# def set_integrator_opt(cfg: Config, integrator: str, **opts) -> Config:
#     """ Set integration options for some integrator type. """
    

def add_pair_param(cfg: Config, potential: str, **opts: dict) -> Config:
    """ Insert pair_param to config after the corresponding pair_potential. """
    idx = [cmd for cmd in cmdidx(cfg, 'pair_potential') if cfg[cmd][1] == potential][0]
    return insert_cmd(cfg, ('pair_param', potential, opts), idx+1)


def contrain_lambda(cfg: Config, P0: float) -> Config:
    """ Contrain junction tension lambda by preferred area P0. 
    This contrain allows us to model the perimeter term as:

    .. math::
        \sum_{i=1}^{\\N} \frac{Gamma}{2}(P_i-P_i^0)^2
    """
    Lambda = -cfg.pair_potential['vp']['gamma']*P0
    return set_cmd_opt(cfg, 'pair_potential', 'vp', **{'lambda': Lambda})
