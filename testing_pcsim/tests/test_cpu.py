from ..pcsim import CPU,ComputerComponent 

def test_cpu():
    cpu = CPU()
    assert cpu.name == 'none' and cpu.speed == 10
    cpu1 = CPU('mrx', 2)
    assert cpu.speed == 10
    

