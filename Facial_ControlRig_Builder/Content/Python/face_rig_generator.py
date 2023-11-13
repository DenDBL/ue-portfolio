# -*- coding: utf-8 -*-
import os
import sys
import collections
import json
import unreal


def load_module():
    unreal.load_module('ControlRigDeveloper')


def create_control_rig_asset(package_path):
    factory = unreal.ControlRigBlueprintFactory()
    return factory.create_new_control_rig_asset(desired_package_path=package_path)


def get_config(config_path):
    if config_path.endswith('.json'):
        with open(config_path, 'r') as f:
            json_data = json.load(f)

        return json_data.get('DRIVER_CONFIG')

    sys.path.append(os.path.dirname(config_path))
    import config

    return config.DRIVER_CONFIG


def get_hierarchy(blueprint):
    return blueprint.hierarchy


def get_hierarchy_controller(blueprint):
    return blueprint.get_hierarchy_controller()


def add_curve(curve_name, blueprint):
    controller = get_hierarchy_controller(blueprint)
    curve = _find_curve(curve_name, blueprint)
    if curve:
        return curve

    return controller.add_curve(curve_name)


def add_forwards_solve_node(blueprint):
    return blueprint.get_controller_by_name('RigVMModel').add_unit_node_from_struct_path(
        '/Script/ControlRig.RigUnit_BeginExecution', 'Execute', unreal.Vector2D(0, -200), 'BeginExecution')


def add_interpolation_node(blueprint, position=(0, 0)):
    library = blueprint.get_local_function_library()
    return blueprint.get_controller_by_name('RigVMModel').add_function_reference_node(
        library.find_function('InterpolateMultipleKeys'), unreal.Vector2D(position[0], position[1]),
        'InterpolateMultipleKeys_1')


def _make_float_array_node(values, blueprint, position=(0, 0)):
    controller = blueprint.get_controller_by_name('RigVMModel')

    array_node = controller.add_array_node(unreal.RigVMOpCode.ARRAY_CLONE,
                                           'float',
                                           None,
                                           unreal.Vector2D(position[0], position[1]),
                                           'ArrayClone')
    for value in values:
        pin = controller.insert_array_pin(f'{array_node.get_node_path()}.Array', -1, '')
        controller.set_pin_default_value(pin, str(value), False)

    return array_node


def _find_variable(name, blueprint):
    variables = blueprint.get_member_variables()
    for variable in variables:
        if variable.name == name:
            return variable


def _find_curve(name, blueprint):
    hierarchy = get_hierarchy(blueprint)

    for curve in hierarchy.get_curves():
        if curve.name == name:
            return curve


def import_and_localize_func(func_path, func_name, blueprint):
    function_blueprint = unreal.load_object(name=func_path, outer=None)

    # blueprint.get_controller_by_name('RigVMModel').add_function_reference_node(
    #     function_blueprint.get_local_function_library().find_function('InterpolateMultipleKeys'),
    #     unreal.Vector2D(-300.000000, -300.000000), func_name)

    blueprint.get_controller_by_name('RigVMModel').localize_functions([unreal.load_object(
        name=func_path, outer=None).get_local_function_library().find_function(
        func_name)], True)


def add_float_variable(variable_name, blueprint, value='0.0'):
    variable = _find_variable(variable_name, blueprint)
    if not variable:
        blueprint.add_member_variable(variable_name, 'double', True, False, value)

    unreal.BlueprintEditorLibrary().set_blueprint_variable_instance_editable(blueprint, variable_name, True)


def add_in_node(in_name, source_type, blueprint, position=(0, 0)):
    controller = blueprint.get_controller_by_name('RigVMModel')

    getter_name = f'GetterNode_{in_name}'

    if 'PARAM' in source_type:
        add_float_variable(in_name, blueprint)

        getter_node = controller.get_graph().find_node_by_name(getter_name)
        if not getter_node:
            getter_node = controller.add_variable_node(in_name, 'double', None, True, '',
                                                       unreal.Vector2D(position[0], position[1]),
                                                       getter_name
                                                       )
    elif 'OUT' in source_type:

        if not _find_curve(in_name, blueprint):
            unreal.log_error(f'Unable to find OUT parameter {in_name}')

        getter_node = controller.add_unit_node_from_struct_path(
            '/Script/ControlRig.RigUnit_GetCurveValue', 'Execute', unreal.Vector2D(position[0], position[1]),
            getter_name)
        controller.set_pin_default_value(f'{getter_node.get_node_path()}.Curve', in_name, False)

    elif 'IN' in source_type:
        if not _find_curve(in_name, blueprint):
            add_curve(in_name, blueprint)

        getter_node = controller.add_unit_node_from_struct_path(
            '/Script/ControlRig.RigUnit_GetCurveValue', 'Execute', unreal.Vector2D(position[0], position[1]),
            getter_name)
        controller.set_pin_default_value(f'{getter_node.get_node_path()}.Curve', in_name, False)

    else:
        raise Exception(f'Incorrect source-value type for {in_name}')

    return getter_node


def add_out_node(out_name, blueprint, position=(0, 0)):
    controller = blueprint.get_controller_by_name('RigVMModel')

    curve = add_curve(out_name, blueprint)
    setter_name = f'SetCurveValue_{out_name}'

    setter_node = controller.add_unit_node_from_struct_path(
        '/Script/ControlRig.RigUnit_SetCurveValue', 'Execute', unreal.Vector2D(position[0], position[1]), setter_name)
    controller.set_pin_default_value(f'{setter_node.get_node_path()}.Curve', curve.name, False)

    return setter_node


def _add_in_driven(in_name, source_type, curve_dict, blueprint, position=(0, 0)):
    controller = blueprint.get_controller_by_name('RigVMModel')
    library = blueprint.get_local_function_library()

    curve_dict = dict(collections.OrderedDict(sorted(curve_dict.items())))

    keys_array = _make_float_array_node(curve_dict.keys(), blueprint, (position[0], position[1]))
    values_array = _make_float_array_node(curve_dict.values(), blueprint, (position[0], position[1] + 50))
    getter_node = add_in_node(in_name, source_type, blueprint, (position[0], position[1] + 100))
    getter_name = getter_node.get_node_path()

    lerp_node = controller.add_function_reference_node(
        library.find_function('InterpolateMultipleKeys'), unreal.Vector2D(position[0] + 150, position[1]),
        f'InterpolateMultipleKeys_{in_name}')

    controller.add_link(f'{keys_array.get_node_path()}.Clone', f'{lerp_node.get_node_path()}.keys')
    controller.add_link(f'{values_array.get_node_path()}.Clone', f'{lerp_node.get_node_path()}.values')
    controller.add_link(f'{getter_name}.Value', f'{lerp_node.get_node_path()}.t_time')

    return lerp_node


def make_connect(in_name, source_type, out_name, blueprint, position=(0, 0)):
    controller = blueprint.get_controller_by_name('RigVMModel')

    sequence_node = controller.add_unit_node_from_struct_path(
        '/Script/ControlRig.RigUnit_SequenceAggregate', 'Execute', unreal.Vector2D(position[0] - 100, position[1]),
        f'SequenceAggregate_{out_name}')
    seq_node_name = sequence_node.get_node_path()
    seq_pin = controller.add_aggregate_pin(seq_node_name, 'END', '')

    getter_node = add_in_node(in_name, source_type, blueprint, position)
    setter_node = add_out_node(out_name, blueprint, position)

    getter_name = getter_node.get_node_path()
    setter_name = setter_node.get_node_path()

    controller.add_link(f'{getter_name}.Value', f'{setter_name}.Value')
    controller.add_link(seq_pin, f'{setter_name}.ExecuteContext')

    controller.add_aggregate_pin(seq_node_name, 'OUT', '')

    return seq_node_name


def make_driven(in_name, source_type, out_name, curve_dict, blueprint, position=(0, 0)):
    controller = blueprint.get_controller_by_name('RigVMModel')
    library = blueprint.get_local_function_library()

    sequence_node = controller.add_unit_node_from_struct_path(
        '/Script/ControlRig.RigUnit_SequenceAggregate', 'Execute', unreal.Vector2D(position[0] - 100, position[1]),
        f'SequenceAggregate_{out_name}')
    seq_node_name = sequence_node.get_node_path()
    seq_pin = controller.add_aggregate_pin(seq_node_name, 'END', '')

    lerp_node = _add_in_driven(in_name, source_type, curve_dict, blueprint, position)
    setter_node = add_out_node(out_name, blueprint, (position[0] + 350, position[1]))
    setter_name = setter_node.get_node_path()

    controller.add_link(f'{lerp_node.get_node_path()}.ExecuteContext', f'{setter_name}.ExecuteContext')
    controller.add_link(f'{lerp_node.get_node_path()}.return', f'{setter_name}.Value')
    controller.add_link(seq_pin, f'{lerp_node.get_node_path()}.ExecuteContext')

    controller.add_aggregate_pin(seq_node_name, 'OUT', '')

    return seq_node_name


def _make_math_for_list(in_list, out_name, template, blueprint, position=(0, 0)):
    controller = blueprint.get_controller_by_name('RigVMModel')

    sequence_node = controller.add_unit_node_from_struct_path(
        '/Script/ControlRig.RigUnit_SequenceAggregate', 'Execute', unreal.Vector2D(position[0] - 100, position[1]),
        'SequenceAggregate')
    seq_node_name = sequence_node.get_node_path()

    math_node = controller.add_template_node(template,
                                             (position[0] + 500, position[1]), f'Math_{out_name}')

    math_node_name = math_node.get_node_path()

    for i, in_item in enumerate(in_list):
        lerp_node = _add_in_driven(in_item[1], in_item[0], in_item[2], blueprint,
                                   (position[0] + 150, position[1] + i * 200))

        seq_pin = controller.add_aggregate_pin(seq_node_name, '', '')
        in_pin = controller.add_aggregate_pin(math_node_name, 'IN_' + str(i), '')
        controller.add_link(seq_pin, f'{lerp_node.get_node_path()}.ExecuteContext')
        controller.add_link(f'{lerp_node.get_node_path()}.return', in_pin)

    setter_node = add_out_node(out_name, blueprint, (position[0] + 650, position[0]))
    setter_name = setter_node.get_node_path()

    seq_pin = controller.add_aggregate_pin(seq_node_name, 'END', '')

    controller.add_link(seq_pin, f'{setter_name}.ExecuteContext')
    controller.add_link(f'{math_node_name}.Result', f'{setter_name}.Value')

    controller.remove_aggregate_pin(f'{math_node_name}.A')
    controller.remove_aggregate_pin(f'{math_node_name}.B')

    controller.add_aggregate_pin(seq_node_name, 'OUT', '')

    return seq_node_name


def make_multiply(in_list, out_name, blueprint, position=(0, 0)):
    return _make_math_for_list(in_list, out_name, 'Multiply::Execute(in A,in B,out Result)', blueprint, position)


def make_sum(in_list, out_name, blueprint, position=(0, 0)):
    return _make_math_for_list(in_list, out_name, 'Add::Execute(in A,in B,out Result)', blueprint, position)


def make_min(in_list, out_name, blueprint, position=(0, 0)):
    return _make_math_for_list(in_list, out_name, 'Minimum::Execute(in A,in B,out Result)', blueprint, position)


def make_max(in_list, out_name, blueprint, position=(0, 0)):
    return _make_math_for_list(in_list, out_name, 'Maximum::Execute(in A,in B,out Result)', blueprint, position)


def make_avg(in_list, out_name, blueprint, position=(0, 0)):
    controller = blueprint.get_controller_by_name('RigVMModel')

    math_sequence_node_path = _make_math_for_list(in_list, out_name, 'Add::Execute(in A,in B,out Result)', blueprint,
                                                  position)

    math_sequence_node = controller.get_graph().find_node(math_sequence_node_path)
    END_pin = math_sequence_node.find_pin(f'END')
    setter_pin = END_pin.get_target_links()[0].get_opposite_pin(END_pin)
    setter_node = setter_pin.get_node()
    setter_value_pin = setter_node.find_pin(f'Value')
    math_pin = setter_value_pin.get_source_links()[0].get_opposite_pin(setter_value_pin)
    math_node = math_pin.get_node()

    controller.break_link(END_pin.get_pin_path(), setter_pin.get_pin_path())
    divide_node = controller.add_template_node('Divide::Execute(in A,in B,out Result)',
                                               unreal.Vector2D(position[0] + 600, position[1] + 100),
                                               f'Divide_{out_name}')

    controller.add_link(math_pin.get_pin_path(), f'{divide_node.get_node_path()}.A')
    controller.set_pin_default_value(f'{divide_node.get_node_path()}.B', str(len(in_list)), False)

    controller.add_link(f'{divide_node.get_node_path()}.Result', f'{setter_node.get_node_path()}.Value')
    controller.add_link(END_pin.get_pin_path(), f'{setter_node.get_node_path()}.ExecuteContext')

    return math_sequence_node.get_node_path()


def _is_IN_parametere(param_tuple):
    return param_tuple[0] == 'IN'


def _has_OUT_parameters(expression):
    param = expression[1]

    if type(param) == list:
        for p in param:
            if not _is_IN_parametere(p):
                return True

    else:
        return not _is_IN_parametere(param)

    return False


def build_expression(out_name, in_tuple, blueprint, position=(0, 0)):
    expression_type = in_tuple[0]

    if expression_type == 'connect':
        expression_list = in_tuple[1]
        in_type = expression_list[0]
        in_name = expression_list[1]

        return make_connect(in_name, in_type, out_name, blueprint, position)
    elif expression_type == "driver":
        expression_list = in_tuple[1]
        in_type = expression_list[0]
        in_name = expression_list[1]
        in_expression = expression_list[2]

        return make_driven(in_name, in_type, out_name, in_expression, blueprint, position)
    elif expression_type == "multiply":
        expression_list = in_tuple[1]

        return make_multiply(expression_list, out_name, blueprint, position)
    elif expression_type == "sum":
        expression_list = in_tuple[1]

        return make_sum(expression_list, out_name, blueprint, position)
    elif expression_type == "average":
        expression_list = in_tuple[1]

        return make_min(expression_list, out_name, blueprint, position)
    elif expression_type == "min":
        expression_list = in_tuple[1]

        return make_avg(expression_list, out_name, blueprint, position)
    elif expression_type == "max":
        expression_list = in_tuple[1]

        return make_max(expression_list, out_name, blueprint, position)
    else:
        raise Exception(f'Incorrect type for {out_name}')


def _build_driver_config(config, blueprint):
    with unreal.ScopedSlowTask(len(config), 'Generating control rig...') as slow_task:
        slow_task.make_dialog(True)
        step = 0

        controller = blueprint.get_controller_by_name('RigVMModel')

        forward_solve_node = controller.add_unit_node_from_struct_path(
            '/Script/ControlRig.RigUnit_BeginExecution', 'Execute', unreal.Vector2D(-300, 0),
            'BeginExecution')

        OUT_pin = forward_solve_node.find_pin('ExecuteContext')

        for i, (key, value) in enumerate(config.items()):
            print(key)
            if not _has_OUT_parameters(value):
                sequence_node_path = build_expression(key, value, blueprint, position=(step * 400, step * 400))
                if not sequence_node_path:
                    continue
                sequence_node = controller.get_graph().find_node(sequence_node_path)

                controller.add_link(OUT_pin.get_pin_path(),
                                    sequence_node.find_pin(f'ExecuteContext').get_pin_path())

                OUT_pin = sequence_node.find_pin(f'OUT')

                step += 1
                slow_task.enter_progress_frame(1)

        for i, (key, value) in enumerate(config.items()):
            print(key)
            if _has_OUT_parameters(value):
                sequence_node_path = build_expression(key, value, blueprint, position=(step * 400, step * 400))
                sequence_node = controller.get_graph().find_node(sequence_node_path)

                controller.add_link(OUT_pin.get_pin_path(),
                                    sequence_node.find_pin(f'ExecuteContext').get_pin_path())
                OUT_pin = sequence_node.find_pin(f'OUT')

                step += 1
                slow_task.enter_progress_frame(1)


def build_control_rig_from_config(config_path, cr_path):
    load_module()
    control_rig = create_control_rig_asset(cr_path)

    import_and_localize_func("/Facial_ControlRig_Builder/ControlRigLib.ControlRigLib", 'InterpolateMultipleKeys',
                             control_rig)
    config = get_config(config_path)

    _build_driver_config(config, control_rig)


if __name__ == '__main__':
    import tkinter as tk
    import tkinter.filedialog as fd

    filetypes = (("JSON-файл", "*.json"),
                 ("Python", "*.py"),
                 ("Любой", "*"))
    filename = fd.askopenfilename(title="Открыть файл", initialdir="/",
                                  filetypes=filetypes)

    if filename:
        build_control_rig_from_config(filename, '/Game/CR_generated')
