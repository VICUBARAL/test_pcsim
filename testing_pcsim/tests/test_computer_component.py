from ..pcsim import ComputerComponent

def test_computer_component():
    cc = ComputerComponent()
    assert cc.name == 'none'
    cc1 = ComputerComponent('pc1')
    assert cc1.name == 'pc1'
    cc2 = ComputerComponent(None)
    assert cc2.name == 'none'
    cc3 = ComputerComponent('Dante Lazzarin')
    assert cc3.name == 'Dante'
    cc4 = ComputerComponent('1223344444555555454534534535345')
    assert cc4.name == '1223344444555555' 
    cc5 = ComputerComponent('')
    assert cc5.name == 'none'
    cc6 = ComputerComponent(' ')
    assert cc6.name == 'none'
    cc7 = ComputerComponent('ll')
    assert cc7.name == 'none'


