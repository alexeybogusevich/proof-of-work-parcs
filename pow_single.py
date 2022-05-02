from Pyro4 import expose
import hashlib
import time

class Solver:
    def __init__(self, workers=None, input_file_name=None, output_file_name=None):
        self.input_file_name = input_file_name
        self.output_file_name = output_file_name
        self.workers = workers
        print("Inited")
    
    def solve(self):
        print("Job Started")
        print("Workers %d" % len(self.workers))

        text, level = self.read_input()

        start_time = time.time()
        hasht, nonce = Solver.proof_of_work(text, level)
        elapsed_time = time.time() - start_time

        print("Main thread has found hash in " + str(elapsed_time) + " seconds.")
        output = Solver.get_proof_of_work_output(level, nonce, hasht, nonce, elapsed_time, 1, 1)
        
        self.write_output(output)

        print("Job Finished")

    def read_input(self):
        f = open(self.input_file_name, 'r')
        text = f.readline()
        level = int(f.readline())
        f.close()
        return text, level

    def write_output(self, output):
        f = open(self.output_file_name, 'w')
        f.write(str(output))
        f.write('\n')
        f.close()

    @staticmethod
    @expose
    def proof_of_work(text, level=1):
        nonce = 1
        count = 0
        leading_zeros = "0" * level
        while True:
            hasht = hashlib.sha256((text + str(nonce)).encode()).hexdigest()    
            if hasht.startswith(leading_zeros):
                return hasht, nonce
            nonce += 1
            count += 1
 
    @staticmethod
    def get_proof_of_work_output(level, nonce, hasht, count, elapsed_time, found_by_worker, workers_number):
        return \
            "Difficulty Level: " + str(level) + '\n' +\
            "Difficulty Mask: " + level * "0" + (64 - level) * "1" + '\n' +\
            "Number of workers: " + str(workers_number) + '\n' +\
            "Solution found by worker: " + str(found_by_worker) + '\n' +\
            "Nonce: " + str(nonce) + '\n' +\
            "Hash: " + str(hasht) + '\n' +\
            str(count) + " hashes in " + str(round(elapsed_time, 10)) + "\n" 