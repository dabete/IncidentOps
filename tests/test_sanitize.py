from sanitize import sanitize_log

def test_sanitize_log():
    log1 = "17/06/09 20:10:41 ERROR Executor: Task 142 in stage 3.0 failed on mesos-slave-07:55904 Traceback request_id=550e8400-e29b-41d4-a716-446655440000 at 0x7ffee3b java.io.IOException: Failed to connect to 10.0.4.12:50010"
    log2 = "18/11/15 08:42:19 ERROR Executor: Task 899 in stage 3.0 failed on mesos-slave-19:42100 Traceback request_id=a1b2c3d4-e5f6-7890-abcd-ef1234567890 at 0x104bc8a java.io.IOException: Failed to connect to 192.168.1.45:8080"

    print(sanitize_log(log1))
    print(sanitize_log(log2))
    assert sanitize_log(log1) == sanitize_log(log2)