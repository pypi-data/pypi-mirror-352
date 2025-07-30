from server import DpipblockServer

def test_dpipblock():
    server = DpipblockServer()
    
    # 测试 port_add
    ip = "192.168.1.1"
    result_add = server.dpfhq_port_management_add(ip)
    print(f"Add result: {result_add}")
    
    # 测试 port_delete
    result_delete = server.dpfhq_port_management_delete(ip)
    print(f"Delete result: {result_delete}")

if __name__ == "__main__":
    test_dpipblock()