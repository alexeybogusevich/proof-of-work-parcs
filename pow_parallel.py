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

        text, level, number_of_workers, nonces_per_worker = self.read_input()
        nonce_start = 0
        start_time = time.time()
        found = False
        mapped = []

        while not found:
            for i in range(0, number_of_workers):
                 mapped.append(self.workers[i].proof_of_work(
                    text, 
                    level, 
                    nonce_start + nonces_per_worker * i,  
                    nonce_start + nonces_per_worker * i + nonces_per_worker))

            reduced = self.myreduce(mapped)

            for result in reduced:
                if result is not None:
                    found = True
                    nonce = result
                    break

            nonce_start += nonces_per_worker * number_of_workers
            mapped = []

        elapsed_time = time.time() - start_time
        print("Wokrer N " + str(i) + " has found hash in " + str(elapsed_time) + " seconds.")

        hasht = Solver.compute_hash(text, nonce)
        found_by_thread = (nonce // nonces_per_worker + 1) % number_of_workers
        output = Solver.get_proof_of_work_output(level, nonce, hasht, nonce, elapsed_time, found_by_thread, number_of_workers)
        self.write_output(output)

        print("Job Finished")

    def read_input(self):
        f = open(self.input_file_name, 'r')
        text = f.readline()
        level = int(f.readline())
        workers = int(f.readline())
        nonces_per_worker = int(f.readline())
        f.close()
        return text, level, workers, nonces_per_worker

    def write_output(self, output):
        f = open(self.output_file_name, 'w')
        f.write(str(output))
        f.write('\n')
        f.close()

    @staticmethod
    @expose
    def proof_of_work(text, level, nonce_start, nonce_end):
        count = 0
        leading_zeros = "0" * level
        for nonce in range(nonce_start, nonce_end):
            hasht = Solver.compute_hash(text, nonce)
            if hasht.startswith(leading_zeros):
                return nonce
            count += 1
        return None
 
    @staticmethod
    def myreduce(mapped):
        output = []
        for x in mapped:
            output.append(x.value)
        return output

    @staticmethod
    def compute_hash(text, nonce):
        return hashlib.sha256((text + str(nonce)).encode()).hexdigest() 

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