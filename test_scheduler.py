from scheduler import Scheduler, PassesFuzz, TrackFuzz, VokoFuzz 
import numpy as np

def test_fuzzification():
    answer = [np.array([0.5 ,0.33333333 ,0.]), np.array([9.93307149e-01, 1.11089965e-02, 2.06115362e-09]), np.array([0,1])]
    sheduler = Scheduler(PassesFuzz, TrackFuzz, VokoFuzz)
    passes, track, voko = sheduler.fuzzification([20], [10], [100], [10])
    print(passes, track, voko)
    assert(np.sum(answer[0] - passes)<1e-6)
    assert(np.sum(answer[1] - track)<1e-6)
    assert(np.sum(answer[2] - voko)<1e-6)
