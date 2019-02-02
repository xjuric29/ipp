from interpret_lib import components
from interpret_lib import instructions


stack = []
frames = components.Frames()
flowControl = components.FlowControl()


def test_vars():
    global stack
    global frames
    global flowControl

    # Definition of global var
    globalVar = instructions.Var('GF@ahoj', frames)
    defvar = instructions.DEFVAR([globalVar], stack, frames, flowControl)
    defvar.exec()

    assert frames.globalFrame == {'ahoj': None}

    # Global var initialization
    const1 = instructions.Const('int', '65')
    move = instructions.MOVE([globalVar, const1], stack, frames, flowControl)
    move.exec()

    assert frames.globalFrame == {'ahoj': 65}

    # Var on tmp frame
    createframe = instructions.CREATEFRAME([], stack, frames, flowControl)
    createframe.exec()

    assert frames.get_frame() == {}

    tmpVar = instructions.Var('TF@_123', frames)
    defvar = instructions.DEFVAR([tmpVar], stack, frames, flowControl)
    defvar.exec()

    assert frames.get_frame() == {'_123': None}
    assert frames.globalFrame == {'ahoj': 65}

    move = instructions.MOVE([tmpVar, globalVar], stack, frames, flowControl)
    move.exec()

    assert frames.get_frame() == {'_123': 65}
    assert frames.globalFrame == {'ahoj': 65}

    # Var on local frame
    pushframe = instructions.PUSHFRAME([], stack, frames, flowControl)
    pushframe.exec()

    assert frames.get_local_frame() == {'_123': 65}

    localVar = instructions.Var('LF@$$$', frames)
    defvar = instructions.DEFVAR([localVar], stack, frames, flowControl)
    defvar.exec()

    assert frames.get_local_frame() == {'_123': 65, '$$$': None}

    const2 = instructions.Const('string', 'ahoj\\032bobo')
    move = instructions.MOVE([localVar, const2], stack, frames, flowControl)
    move.exec()

    assert frames.get_local_frame() == {'_123': 65, '$$$': 'ahoj bobo'}

    # Back on tmp frame
    popframe = instructions.POPFRAME([], stack, frames, flowControl)
    popframe.exec()

    assert frames.get_frame() == {'_123': 65, '$$$': 'ahoj bobo'}


def test_labels():
    global stack
    global frames
    global flowControl

    label = instructions.Label('novicok')
    flowControl.instructionCounter = 200
    labelInst = instructions.LABEL([label], stack, frames, flowControl)
    labelInst.exec()

    assert flowControl.labelDict['novicok'] == 200

    flowControl.instructionCounter = 1
    call = instructions.CALL([label], stack, frames, flowControl)
    call.exec()

    assert flowControl.positionStack == [1]
    assert flowControl.instructionCounter == 200

    ret = instructions.RETURN([], stack, frames, flowControl)
    ret.exec()

    assert flowControl.positionStack == []
    assert flowControl.instructionCounter == 1


def test_stack():
    global stack
    global frames
    global flowControl

    globalVar = instructions.Var('GF@prom', frames)
    globalVar.define()
    globalVar.set_value(True)
    const = instructions.Const('int', '42')
    pushs = instructions.PUSHS([globalVar], stack, frames, flowControl)
    pushs.exec()

    assert stack == [True]

    pushs = instructions.PUSHS([const], stack, frames, flowControl)
    pushs.exec()

    assert stack == [True, 42]

    pops = instructions.POPS([globalVar], stack, frames, flowControl)
    pops.exec()

    assert stack == [True]
    assert globalVar.get_value() == 42

    pops.exec()

    assert stack == []
    assert globalVar.get_value() is True


def test_arithmetic_operation_add():
    global stack
    global frames
    global flowControl

    globalVar1 = instructions.Var('GF@var1', frames)
    globalVar1.define()
    globalVar1.set_value(20)
    globalVar2 = instructions.Var('GF@var2', frames)
    globalVar2.define()
    globalVar2.set_value(40)
    globalVar3 = instructions.Var('GF@result', frames)
    globalVar3.define()
    const1 = instructions.Const('int', '42')
    const2 = instructions.Const('int', '4')

    # For vars
    add = instructions.ADD([globalVar3, globalVar1, globalVar2], stack, frames, flowControl)
    add.exec()

    assert globalVar3.get_value() == 60

    # For constants
    add = instructions.ADD([globalVar3, const1, const2], stack, frames, flowControl)
    add.exec()

    assert globalVar3.get_value() == 46

    # For var and constant
    add = instructions.ADD([globalVar3, globalVar1, const1], stack, frames, flowControl)
    add.exec()

    assert globalVar3.get_value() == 62


def test_arithmetic_operation_sub():
    global stack
    global frames
    global flowControl

    globalVar1 = instructions.Var('GF@var1', frames)
    globalVar1.define()
    globalVar1.set_value(20)
    globalVar2 = instructions.Var('GF@var2', frames)
    globalVar2.define()
    globalVar2.set_value(40)
    globalVar3 = instructions.Var('GF@result', frames)
    globalVar3.define()
    const1 = instructions.Const('int', '42')
    const2 = instructions.Const('int', '4')

    # For vars
    sub = instructions.SUB([globalVar3, globalVar1, globalVar2], stack, frames, flowControl)
    sub.exec()

    assert globalVar3.get_value() == -20

    # For constants
    sub = instructions.SUB([globalVar3, const1, const2], stack, frames, flowControl)
    sub.exec()

    assert globalVar3.get_value() == 38

    # For var and constant
    sub = instructions.SUB([globalVar3, globalVar1, const1], stack, frames, flowControl)
    sub.exec()

    assert globalVar3.get_value() == -22


def test_arithmetic_operation_mul():
    global stack
    global frames
    global flowControl

    globalVar1 = instructions.Var('GF@var1', frames)
    globalVar1.define()
    globalVar1.set_value(20)
    globalVar2 = instructions.Var('GF@var2', frames)
    globalVar2.define()
    globalVar2.set_value(40)
    globalVar3 = instructions.Var('GF@result', frames)
    globalVar3.define()
    const1 = instructions.Const('int', '42')
    const2 = instructions.Const('int', '4')

    # For vars
    mul = instructions.MUL([globalVar3, globalVar1, globalVar2], stack, frames, flowControl)
    mul.exec()

    assert globalVar3.get_value() == 800

    # For constants
    mul = instructions.MUL([globalVar3, const1, const2], stack, frames, flowControl)
    mul.exec()

    assert globalVar3.get_value() == 168

    # For var and constant
    mul = instructions.MUL([globalVar3, globalVar1, const1], stack, frames, flowControl)
    mul.exec()

    assert globalVar3.get_value() == 840


def test_arithmetic_operation_idiv():
    global stack
    global frames
    global flowControl

    globalVar1 = instructions.Var('GF@var1', frames)
    globalVar1.define()
    globalVar1.set_value(20)
    globalVar2 = instructions.Var('GF@var2', frames)
    globalVar2.define()
    globalVar2.set_value(40)
    globalVar3 = instructions.Var('GF@result', frames)
    globalVar3.define()
    const1 = instructions.Const('int', '42')
    const2 = instructions.Const('int', '4')

    # For vars
    idiv = instructions.IDIV([globalVar3, globalVar1, globalVar2], stack, frames, flowControl)
    idiv.exec()

    assert globalVar3.get_value() == 0

    # For constants
    idiv = instructions.IDIV([globalVar3, const1, const2], stack, frames, flowControl)
    idiv.exec()

    assert globalVar3.get_value() == 10

    # For var and constant
    idiv = instructions.IDIV([globalVar3, globalVar1, const1], stack, frames, flowControl)
    idiv.exec()

    assert globalVar3.get_value() == 0


def test_relation_operations():
    global stack
    global frames
    global flowControl

    globalVar3 = instructions.Var('GF@result1', frames)
    globalVar3.define()
    globalVar4 = instructions.Var('GF@result2', frames)
    globalVar4.define()
    globalVar5 = instructions.Var('GF@result3', frames)
    globalVar5.define()

    # Int relations
    const1 = instructions.Const('int', '42')
    const2 = instructions.Const('int', '4')
    globalVar1 = instructions.Var('GF@var1', frames)
    globalVar1.define()
    globalVar1.set_value(20)
    globalVar2 = instructions.Var('GF@var2', frames)
    globalVar2.define()
    globalVar2.set_value(20)

    lt = instructions.LT([globalVar3, const1, const2], stack, frames, flowControl)
    lt.exec()
    gt = instructions.GT([globalVar4, const1, const2], stack, frames, flowControl)
    gt.exec()
    eq = instructions.EQ([globalVar5, const1, const2], stack, frames, flowControl)
    eq.exec()

    assert globalVar3.get_value() is False
    assert globalVar4.get_value() is True
    assert globalVar5.get_value() is False

    lt = instructions.LT([globalVar3, const2, const1], stack, frames, flowControl)
    lt.exec()
    gt = instructions.GT([globalVar4, const2, const1], stack, frames, flowControl)
    gt.exec()
    eq = instructions.EQ([globalVar5, globalVar2, globalVar1], stack, frames, flowControl)
    eq.exec()

    assert globalVar3.get_value() is True
    assert globalVar4.get_value() is False
    assert globalVar5.get_value() is True

    # Bool relations
    const1 = instructions.Const('bool', 'true')
    const2 = instructions.Const('bool', 'false')
    globalVar1 = instructions.Var('GF@var1', frames)
    globalVar1.define()
    globalVar1.set_value(True)
    globalVar2 = instructions.Var('GF@var2', frames)
    globalVar2.define()
    globalVar2.set_value(True)

    lt = instructions.LT([globalVar3, const1, const2], stack, frames, flowControl)
    lt.exec()
    gt = instructions.GT([globalVar4, const1, const2], stack, frames, flowControl)
    gt.exec()
    eq = instructions.EQ([globalVar5, const1, const2], stack, frames, flowControl)
    eq.exec()

    assert globalVar3.get_value() is False
    assert globalVar4.get_value() is True
    assert globalVar5.get_value() is False

    lt = instructions.LT([globalVar3, const2, const1], stack, frames, flowControl)
    lt.exec()
    gt = instructions.GT([globalVar4, const2, const1], stack, frames, flowControl)
    gt.exec()
    eq = instructions.EQ([globalVar5, globalVar2, globalVar1], stack, frames, flowControl)
    eq.exec()

    assert globalVar3.get_value() is True
    assert globalVar4.get_value() is False
    assert globalVar5.get_value() is True

    # String relations
    const1 = instructions.Const('string', 'ahojda')
    const2 = instructions.Const('string', 'ahoj')
    globalVar1 = instructions.Var('GF@var1', frames)
    globalVar1.define()
    globalVar1.set_value('hoj')
    globalVar2 = instructions.Var('GF@var2', frames)
    globalVar2.define()
    globalVar2.set_value('hoj')

    lt = instructions.LT([globalVar3, const1, const2], stack, frames, flowControl)
    lt.exec()
    gt = instructions.GT([globalVar4, const1, const2], stack, frames, flowControl)
    gt.exec()
    eq = instructions.EQ([globalVar5, const1, const2], stack, frames, flowControl)
    eq.exec()

    assert globalVar3.get_value() is False
    assert globalVar4.get_value() is True
    assert globalVar5.get_value() is False

    lt = instructions.LT([globalVar3, const2, const1], stack, frames, flowControl)
    lt.exec()
    gt = instructions.GT([globalVar4, const2, const1], stack, frames, flowControl)
    gt.exec()
    eq = instructions.EQ([globalVar5, globalVar2, globalVar1], stack, frames, flowControl)
    eq.exec()

    assert globalVar3.get_value() is True
    assert globalVar4.get_value() is False
    assert globalVar5.get_value() is True


def test_logical_operation_and():
    global stack
    global frames
    global flowControl

    globalVar1 = instructions.Var('GF@var1', frames)
    globalVar1.define()
    globalVar1.set_value(True)
    globalVar2 = instructions.Var('GF@var2', frames)
    globalVar2.define()
    globalVar2.set_value(True)
    globalVar3 = instructions.Var('GF@result1', frames)

    const1 = instructions.Const('bool', 'false')
    const2 = instructions.Const('bool', 'false')

    # For vars
    logAnd = instructions.AND([globalVar3, globalVar1, globalVar2], stack, frames, flowControl)
    logAnd.exec()

    assert globalVar3.get_value() is True

    # For constants
    logAnd = instructions.AND([globalVar3, const1, const2], stack, frames, flowControl)
    logAnd.exec()

    assert globalVar3.get_value() is False

    # For constant and var
    logAnd = instructions.AND([globalVar3, const1, globalVar1], stack, frames, flowControl)
    logAnd.exec()

    assert globalVar3.get_value() is False


def test_logical_operation_or():
    global stack
    global frames
    global flowControl

    globalVar1 = instructions.Var('GF@var1', frames)
    globalVar1.define()
    globalVar1.set_value(True)
    globalVar2 = instructions.Var('GF@var2', frames)
    globalVar2.define()
    globalVar2.set_value(True)
    globalVar3 = instructions.Var('GF@result1', frames)

    const1 = instructions.Const('bool', 'false')
    const2 = instructions.Const('bool', 'false')

    # For vars
    logOr = instructions.OR([globalVar3, globalVar1, globalVar2], stack, frames, flowControl)
    logOr.exec()

    assert globalVar3.get_value() is True

    # For constants
    logOr = instructions.OR([globalVar3, const1, const2], stack, frames, flowControl)
    logOr.exec()

    assert globalVar3.get_value() is False

    # For constant and var
    logOr = instructions.OR([globalVar3, const1, globalVar1], stack, frames, flowControl)
    logOr.exec()

    assert globalVar3.get_value() is True


def test_logical_operation_not():
    global stack
    global frames
    global flowControl

    globalVar1 = instructions.Var('GF@var1', frames)
    globalVar1.define()
    globalVar1.set_value(True)
    globalVar2 = instructions.Var('GF@result1', frames)

    const = instructions.Const('bool', 'false')

    # For vars
    logNot = instructions.NOT([globalVar2, globalVar1], stack, frames, flowControl)
    logNot.exec()

    assert globalVar2.get_value() is False

    # For constants
    logNot = instructions.NOT([globalVar2, const], stack, frames, flowControl)
    logNot.exec()

    assert globalVar2.get_value() is True


def test_string_operation_int2char():
    global stack
    global frames
    global flowControl

    globalVar1 = instructions.Var('GF@var1', frames)
    globalVar1.define()
    globalVar1.set_value(65)
    globalVar2 = instructions.Var('GF@result1', frames)

    const = instructions.Const('int', '32')

    # For vars
    int2char = instructions.INT2CHAR([globalVar2, globalVar1], stack, frames, flowControl)
    int2char.exec()

    assert globalVar2.get_value() is 'A'

    # For constants
    int2char = instructions.INT2CHAR([globalVar2, const], stack, frames, flowControl)
    int2char.exec()

    assert globalVar2.get_value() is ' '


def test_string_operation_int2char():
    global stack
    global frames
    global flowControl

    globalVar1 = instructions.Var('GF@var1', frames)
    globalVar1.define()
    globalVar1.set_value(65)
    globalVar2 = instructions.Var('GF@result1', frames)
    globalVar2.define()

    const = instructions.Const('int', '32')

    # For vars
    int2char = instructions.INT2CHAR([globalVar2, globalVar1], stack, frames, flowControl)
    int2char.exec()

    assert globalVar2.get_value() == 'A'

    # For constants
    int2char = instructions.INT2CHAR([globalVar2, const], stack, frames, flowControl)
    int2char.exec()

    assert globalVar2.get_value() == ' '


def test_string_operation_stri2int():
    global stack
    global frames
    global flowControl

    globalVar1 = instructions.Var('GF@var1', frames)
    globalVar1.define()
    globalVar1.set_value('Ahoj')
    globalVar2 = instructions.Var('GF@var2', frames)
    globalVar2.define()
    globalVar2.set_value(0)
    globalVar3 = instructions.Var('GF@result1', frames)
    globalVar3.define()

    const1 = instructions.Const('string', 'A\\032')
    const2 = instructions.Const('int', '1')

    # For vars
    stri2int = instructions.STRI2INT([globalVar3, globalVar1, globalVar2], stack, frames, flowControl)
    stri2int.exec()

    assert globalVar3.get_value() == 65

    # For constants
    stri2int = instructions.STRI2INT([globalVar3, const1, const2], stack, frames, flowControl)
    stri2int.exec()

    assert globalVar3.get_value() == 32


def test_string_operation_concat():
    global stack
    global frames
    global flowControl

    globalVar1 = instructions.Var('GF@var1', frames)
    globalVar1.define()
    globalVar1.set_value('Ahoj ')
    globalVar2 = instructions.Var('GF@var2', frames)
    globalVar2.define()
    globalVar2.set_value('svete')
    globalVar3 = instructions.Var('GF@result1', frames)
    globalVar3.define()

    const1 = instructions.Const('string', 'Jay')
    const2 = instructions.Const('string', 'Jay')

    # For vars
    concat = instructions.CONCAT([globalVar3, globalVar1, globalVar2], stack, frames, flowControl)
    concat.exec()

    assert globalVar3.get_value() == 'Ahoj svete'

    # For constants
    concat = instructions.CONCAT([globalVar3, const1, const2], stack, frames, flowControl)
    concat.exec()

    assert globalVar3.get_value() == 'JayJay'


def test_string_operation_strlen():
    global stack
    global frames
    global flowControl

    globalVar1 = instructions.Var('GF@var1', frames)
    globalVar1.define()
    globalVar1.set_value('ahoj')
    globalVar2 = instructions.Var('GF@result1', frames)
    globalVar2.define()

    const = instructions.Const('string', 'ahojda')

    # For vars
    strlen = instructions.STRLEN([globalVar2, globalVar1], stack, frames, flowControl)
    strlen.exec()

    assert globalVar2.get_value() == 4

    # For constants
    strlen = instructions.STRLEN([globalVar2, const], stack, frames, flowControl)
    strlen.exec()

    assert globalVar2.get_value() == 6


def test_string_operation_getchar():
    global stack
    global frames
    global flowControl

    globalVar1 = instructions.Var('GF@var1', frames)
    globalVar1.define()
    globalVar1.set_value('Ahoj')
    globalVar2 = instructions.Var('GF@var2', frames)
    globalVar2.define()
    globalVar2.set_value(3)
    globalVar3 = instructions.Var('GF@result1', frames)
    globalVar3.define()

    const1 = instructions.Const('string', 'Jay')
    const2 = instructions.Const('int', '0')

    # For vars
    getchar = instructions.GETCHAR([globalVar3, globalVar1, globalVar2], stack, frames, flowControl)
    getchar.exec()

    assert globalVar3.get_value() == 'j'

    # For constants
    getchar = instructions.GETCHAR([globalVar3, const1, const2], stack, frames, flowControl)
    getchar.exec()

    assert globalVar3.get_value() == 'J'


def test_string_operation_setchar():
    global stack
    global frames
    global flowControl

    globalVar1 = instructions.Var('GF@var1', frames)
    globalVar1.define()
    globalVar1.set_value(3)
    globalVar2 = instructions.Var('GF@var2', frames)
    globalVar2.define()
    globalVar2.set_value('o')
    globalVar3 = instructions.Var('GF@result1', frames)
    globalVar3.define()
    globalVar3.set_value('mozek')

    const1 = instructions.Const('int', '4')
    const2 = instructions.Const('string', 'l')

    # For vars
    getchar = instructions.SETCHAR([globalVar3, globalVar1, globalVar2], stack, frames, flowControl)
    getchar.exec()

    assert globalVar3.get_value() == 'mozok'

    # For constants
    getchar = instructions.SETCHAR([globalVar3, const1, const2], stack, frames, flowControl)
    getchar.exec()

    assert globalVar3.get_value() == 'mozol'


def test_type():
    global stack
    global frames
    global flowControl

    globalVar1 = instructions.Var('GF@var1', frames)
    globalVar1.define()
    globalVar1.set_value(True)
    globalVar2 = instructions.Var('GF@result1', frames)
    globalVar2.define()

    const1 = instructions.Const('int', '4')
    const2 = instructions.Const('string', 'l')

    # For vars
    instType = instructions.TYPE([globalVar2, globalVar1], stack, frames, flowControl)
    instType.exec()

    assert globalVar2.get_value() == 'bool'

    # For constants
    instType = instructions.TYPE([globalVar2, const1], stack, frames, flowControl)
    instType.exec()

    assert globalVar2.get_value() == 'int'

    instType = instructions.TYPE([globalVar2, const2], stack, frames, flowControl)
    instType.exec()

    assert globalVar2.get_value() == 'string'


def test_jump():
    global stack
    global frames
    global flowControl

    labelT = instructions.Label('label')
    label = instructions.LABEL([labelT], stack, frames, flowControl)
    label.exec()

    assert flowControl.labelDict['label'] == 1

    flowControl.instructionCounter = 200
    jump = instructions.JUMP([labelT], stack, frames, flowControl)
    jump.exec()

    assert flowControl.labelDict['label'] == 1
    assert flowControl.instructionCounter == 1


def test_jumpifeq():
    global stack
    global frames
    global flowControl

    flowControl = components.FlowControl()

    globalVar1 = instructions.Var('GF@var1', frames)
    globalVar1.define()
    globalVar1.set_value(True)
    globalVar2 = instructions.Var('GF@result1', frames)
    globalVar2.define()
    globalVar2.set_value(False)

    const1 = instructions.Const('int', '4')
    const2 = instructions.Const('int', '5')
    const3 = instructions.Const('string', 'ahoj')
    const4 = instructions.Const('string', 'ahojda')

    labelT = instructions.Label('label')
    label = instructions.LABEL([labelT], stack, frames, flowControl)
    label.exec()

    # Vars bool
    flowControl.instructionCounter = 200
    jumpifeq = instructions.JUMPIFEQ([labelT, globalVar1, globalVar1], stack, frames, flowControl)
    jumpifeq.exec()

    assert flowControl.instructionCounter == 0

    flowControl.instructionCounter = 200
    jumpifeq = instructions.JUMPIFEQ([labelT, globalVar1, globalVar2], stack, frames, flowControl)
    jumpifeq.exec()

    assert flowControl.instructionCounter == 200

    # Constants int
    flowControl.instructionCounter = 200
    jumpifeq = instructions.JUMPIFEQ([labelT, const1, const1], stack, frames, flowControl)
    jumpifeq.exec()

    assert flowControl.instructionCounter == 0

    flowControl.instructionCounter = 200
    jumpifeq = instructions.JUMPIFEQ([labelT, const1, const2], stack, frames, flowControl)
    jumpifeq.exec()

    assert flowControl.instructionCounter == 200

    # Constants sting
    flowControl.instructionCounter = 200
    jumpifeq = instructions.JUMPIFEQ([labelT, const3, const3], stack, frames, flowControl)
    jumpifeq.exec()

    assert flowControl.instructionCounter == 0

    flowControl.instructionCounter = 200
    jumpifeq = instructions.JUMPIFEQ([labelT, const3, const4], stack, frames, flowControl)
    jumpifeq.exec()

    assert flowControl.instructionCounter == 200


def test_jumpifneq():
    global stack
    global frames
    global flowControl

    flowControl = components.FlowControl()

    globalVar1 = instructions.Var('GF@var1', frames)
    globalVar1.define()
    globalVar1.set_value(True)
    globalVar2 = instructions.Var('GF@result1', frames)
    globalVar2.define()
    globalVar2.set_value(False)

    const1 = instructions.Const('int', '4')
    const2 = instructions.Const('int', '5')
    const3 = instructions.Const('string', 'ahoj')
    const4 = instructions.Const('string', 'ahojda')

    labelT = instructions.Label('label')
    label = instructions.LABEL([labelT], stack, frames, flowControl)
    label.exec()

    # Vars bool
    flowControl.instructionCounter = 200
    jumpifneq = instructions.JUMPIFNEQ([labelT, globalVar1, globalVar1], stack, frames, flowControl)
    jumpifneq.exec()

    assert flowControl.instructionCounter == 200

    flowControl.instructionCounter = 200
    jumpifneq = instructions.JUMPIFNEQ([labelT, globalVar1, globalVar2], stack, frames, flowControl)
    jumpifneq.exec()

    assert flowControl.instructionCounter == 0

    # Constants int
    flowControl.instructionCounter = 200
    jumpifneq = instructions.JUMPIFNEQ([labelT, const1, const1], stack, frames, flowControl)
    jumpifneq.exec()

    assert flowControl.instructionCounter == 200

    flowControl.instructionCounter = 200
    jumpifneq = instructions.JUMPIFNEQ([labelT, const1, const2], stack, frames, flowControl)
    jumpifneq.exec()

    assert flowControl.instructionCounter == 0

    # Constants sting
    flowControl.instructionCounter = 200
    jumpifneq = instructions.JUMPIFNEQ([labelT, const3, const3], stack, frames, flowControl)
    jumpifneq.exec()

    assert flowControl.instructionCounter == 200

    flowControl.instructionCounter = 200
    jumpifneq = instructions.JUMPIFNEQ([labelT, const3, const4], stack, frames, flowControl)
    jumpifneq.exec()

    assert flowControl.instructionCounter == 0
