from src.stata_config import stata
from tqdm import tqdm
from typing import Optional
import random
import math
import argparse
import re


class PyOneclick:
    def __init__(
            self,
            z_statistic: bool,
            threshold: Optional[float],
            iterations: int,
            initial_temperature: float,
            min_temperature: float,
            cooling_rate: float,
            max_steps: int
    ):
        self._z_statistic = z_statistic
        self._threshold = threshold
        self._iterations = iterations
        self._initial_temperature = initial_temperature
        self._min_temperature = min_temperature
        self._cooling_rate = cooling_rate
        self._max_steps = max_steps

    def target_function(
            self,
            sel_lst: list[bool],
            ctrl_lst: list[str],
            stata_cmds: list[dict[str, str]]
    ) -> list[float]:

        _p_values = []
        for _stata_cmd in stata_cmds:
            _sel_ctrl_lst = [ctrl_lst[i] for i in range(len(ctrl_lst)) if sel_lst[i]]
            _sel_ctrl_vars = ' '.join(_sel_ctrl_lst)
            stata.run('global CONTROL_VARIABLES ' + _sel_ctrl_vars, quietly=True)
            stata.run(
                f'{_stata_cmd['method']} {_stata_cmd["dependent"]} {_stata_cmd["adjust"]} {_stata_cmd["fixed"]} '
                + f'$CONTROL_VARIABLES {_stata_cmd["others"]}',
                quietly=True
            )
            if not self._z_statistic:
                stata.run(
                    f'gen P_VALUE = 2 * ttail(e(df_r), abs(_b[{_stata_cmd['adjust']}]/_se[{_stata_cmd['adjust']}]))',
                    quietly=True
                )
            else:
                stata.run(
                    f'gen P_VALUE = 2 * (1-normal(abs(_b[{_stata_cmd['adjust']}]/_se[{_stata_cmd['adjust']}])))',
                    quietly=True
                )
            _p_value = stata.pdataframe_from_data(var=['P_VALUE']).at[0, 'P_VALUE']
            _p_values.append(_p_value)
            stata.run('drop P_VALUE', quietly=True)
        return _p_values

    def _p_vals_diff(
            self,
            _lst1: list[float],
            _lst2: list[float]
    ) -> float:

        if self._threshold is None:
            _sum1 = sum(_lst1)
            _sum2 = sum(_lst2)
        else:
            _sum1 = sum(_lst1) if all(_item < self._threshold for _item in _lst1) \
                else sum(max(_item, self._threshold) for _item in _lst1)
            _sum2 = sum(_lst2) if all(_item < self._threshold for _item in _lst2) \
                else sum(max(_item, self._threshold) for _item in _lst2)
        return _sum1 - _sum2

    def _p_vals_less(
            self,
            _lst1: list[float],
            _lst2: list[float]
    ) -> bool:

        return self._p_vals_diff(_lst1, _lst2) < 0

    def _simulated_annealing(
            self,
            _func: callable,
            _x: list[bool],
            _ctrl: list[str],
            _cmds: list[dict[str, str]],
    ) -> tuple[list[bool], list[float]]:

        _current_x = _x.copy()
        _current_vals = _func(_current_x, _ctrl, _cmds)
        _best_x = _current_x.copy()
        _best_vals = _current_vals
        _temperature = self._initial_temperature
        for _ in tqdm(
                range(self._max_steps),
                bar_format='{l_bar}{bar}| {n_fmt}/{total_fmt} [{rate_fmt} ]',
                desc="Searching",
                ncols=100,
                unit=" step",
                leave=False
        ):
            if _temperature < self._min_temperature:
                break
            _new_x = _current_x.copy()
            _flip_index = random.randint(0, len(_new_x) - 1)
            _new_x[_flip_index] = not _new_x[_flip_index]
            _new_vals = _func(_new_x, _ctrl, _cmds)
            _delta_e = self._p_vals_diff(_new_vals, _current_vals)
            if _delta_e < 0:
                _current_x = _new_x
                _current_vals = _new_vals
                if self._p_vals_less(_current_vals, _best_vals):
                    _best_x = _current_x.copy()
                    _best_vals = _current_vals
            else:
                _acceptance_prob = math.exp(-_delta_e / _temperature)
                if random.random() < _acceptance_prob:
                    _current_x = _new_x
                    _current_vals = _new_vals
            _temperature *= self._cooling_rate
        return _best_x, _best_vals

    @staticmethod
    def print_commands(
            stata_commands: list[str]
    ) -> None:

        print("-" * 100 + '\n')
        for _index, _stata_command in enumerate(stata_commands):
            print(f"Command: {_index} |")
            print(f"method: {_stata_command['method']} | dependent: {_stata_command['dependent']} | " +
                  f"adjust: {_stata_command['adjust']} | fixed: {_stata_command['fixed']}")
            print(f"control: {_stata_command['control']}")
            print(f"others: {_stata_command['others']}")
        print('\n' + "-" * 100 + '\n')

    @staticmethod
    def print_result(
            guiding_words: str,
            p_values: list[float],
            selected_variables: str,
            stata_commands: list[dict[str, str]],
    ) -> None:

        _new_full_commands = []
        for _stata_command in stata_commands:
            _new_full_command = (
                    f"{_stata_command['method']} {_stata_command['dependent']} {_stata_command['adjust']} " +
                    f"{_stata_command['fixed']} {selected_variables} {_stata_command['others']}"
            )
            _new_full_command = re.sub(r'\s+', ' ', _new_full_command)
            _new_full_command = re.sub(r'\s+,', ',', _new_full_command)
            _new_full_commands.append(_new_full_command)
        print(guiding_words + " | ", end="")
        if len(p_values) > 1:
            print()
        for _p_val, _new_full_command in zip(p_values, _new_full_commands):
            print(f"p-value: {_p_val:.6f} | {_new_full_command}")
        if len(p_values) > 1:
            print()

    def search(
            self,
            dta_path: str,
            stata_commands: list[dict[str, str]]
    ) -> tuple[list[float], str]:

        stata.run(f'use "{dta_path}"', quietly=True)
        _initial_ctrl_vars = stata_commands[0]['control']
        _initial_ctrl_lst = _initial_ctrl_vars.split(sep=' ')
        _initial_sel_list = [True] * len(_initial_ctrl_lst)
        _best_p_vals = [1] * len(stata_commands)
        _best_sel_lst = _initial_sel_list
        for iteration in range(self._iterations):
            _new_sel_lst, _new_p_vals = self._simulated_annealing(
                self.target_function, _initial_sel_list, _initial_ctrl_lst, stata_commands
            )
            if self._p_vals_less(_new_p_vals, _best_p_vals):
                _best_sel_lst = _new_sel_lst
                _best_p_vals = _new_p_vals
            _new_selected_vars = ' '.join(
                [_initial_ctrl_lst[i] for i in range(len(_initial_ctrl_lst)) if _new_sel_lst[i]]
            )
            self.print_result(f"Iter: {iteration+1}", _new_p_vals, _new_selected_vars, stata_commands)
        _best_sel_vars = ' '.join(
            [_initial_ctrl_lst[i] for i in range(len(_initial_ctrl_lst)) if _best_sel_lst[i]]
        )
        return _best_p_vals, _best_sel_vars


def main() -> None:

    # Parameter parsing
    parser = argparse.ArgumentParser(description='Pyoneclick Parameter Parser')
    parser.add_argument('-d', '--data', required=True,
                        help='Data file path')
    parser.add_argument('-a', '--adjust', action='append', default=None,
                        help='Independent variable that need to be adjusted')
    parser.add_argument('-f', '--fixed', action='append', default=None,
                        help='Fixed independent variable')
    parser.add_argument('-c', '--command', action='append', required=True,
                        help='Full regression command')
    parser.add_argument('-z', '--z_statistic', action='store_true',
                        help='Z-statistic mode')
    parser.add_argument('-t', '--threshold', type=float, default=None,
                        help='Threshold for p-value')
    parser.add_argument('--iterations', type=int, default=5,
                        help='Number of iterations')
    parser.add_argument('--initial_temperature', type=float, default=1e2,
                        help='Initial temperature for simulated annealing')
    parser.add_argument('--min_temperature', type=float, default=1e-8,
                        help='Minimum temperature for simulated annealing')
    parser.add_argument('--cooling_rate', type=float, default=0.90,
                        help='Cooling rate for simulated annealing')
    parser.add_argument('--max_steps', type=int, default=200,
                        help='Maximum steps for simulated annealing')
    parser.add_argument('-p', '--print_commands', action='store_true',
                        help='Print commands')
    args = parser.parse_args()

    # Parse command-line arguments
    data: str = args.data
    _full_commands: list[str] = args.command
    _adjust_vars: Optional[list[str]] = args.adjust
    _fixed_vars: Optional[list[str]] = args.fixed
    _adjust_vars_len = len(_adjust_vars) if _adjust_vars is not None else 0
    _fixed_vars_len = len(_fixed_vars) if _fixed_vars is not None else 0
    if len(_full_commands) == 1:
        _full_commands = [_full_commands[0]] * max(len(_full_commands), max(_adjust_vars_len, _fixed_vars_len))
    commands: list[dict[str, str]] = []
    for _index, _full_command in enumerate(_full_commands):
        if 'if' in _full_command:
            _full_command_list: list[str] = _full_command.split(sep='if')
            _full_command_list[1] = 'if' + _full_command_list[1]
        else:
            _full_command_list: list[str] = _full_command.split(sep=',')
            _full_command_list[1] = ',' + _full_command_list[1]
        _main_command: str = _full_command_list[0]
        _others: str = _full_command_list[1]
        _main_command_list: list[str] = _main_command.split(sep=' ')
        _method: str = _main_command_list[0]
        _dependent: str = _main_command_list[1]
        if _adjust_vars is None:
            _adjust: str = _main_command_list[2]
        elif len(_adjust_vars) == 1:
            _adjust: str = _adjust_vars[0]
        else:
            _adjust: str = _adjust_vars[_index]
        _adjust_list = _adjust.split(sep=' ')
        if _fixed_vars is None:
            _fixed: str = ""
        elif len(_fixed_vars) == 1:
            _fixed: str = _fixed_vars[0]
        else:
            _fixed: str = _fixed_vars[_index]
        _fixed = _fixed.replace(" ", "")
        _fixed_list = _fixed.split(sep=' ')
        _control_list: list[str] = \
            [item for item in _main_command_list if item not in [_method]+[_dependent]+_adjust_list+_fixed_list]
        _control: str = ' '.join(_control_list)
        command: dict[str, str] = {
            'method': _method,
            'dependent': _dependent,
            'adjust': _adjust,
            'fixed': _fixed,
            'control': _control,
            'others': _others
        }
        commands.append(command)
    if args.print_commands:
        PyOneclick.print_commands(commands)

    # Initialize class instance
    oneclick = PyOneclick(
        z_statistic=args.z_statistic,
        threshold=args.threshold,
        iterations=args.iterations,
        initial_temperature=args.initial_temperature,
        min_temperature=args.min_temperature,
        cooling_rate=args.cooling_rate,
        max_steps=args.max_steps
    )

    # Execute command
    best_p_values, best_control_variables = oneclick.search(data, commands)
    print("-" * 100 + '\n')
    PyOneclick.print_result("best result", best_p_values, best_control_variables, commands)
    print("-" * 100 + '\n')


if __name__ == "__main__":
    main()


