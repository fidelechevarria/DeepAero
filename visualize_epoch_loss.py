import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

RUN = 5

runs = ['A', 'B', 'C', 'D', 'E', 'F']
names = ['gru_256', 'gru_1024', 'lstm', 'lstm_1500_epochs', 'lstm_pos_quat_ri', 'lstm_random_init']

train = pd.read_csv('results/' + names[RUN] + '/run-train-tag-epoch_loss.csv')
val = pd.read_csv('results/' + names[RUN] + '/run-validation-tag-epoch_loss.csv')

train = train.apply(lambda x: np.unwrap(x, discont=10) if x.name == 'Step' else x)
val = val.apply(lambda x: np.unwrap(x, discont=10) if x.name == 'Step' else x)

fig = plt.figure()
ax = fig.add_subplot(1, 1, 1)
ax.plot(train['Step'], train['Value'], label='Train')
ax.plot(val['Step'], val['Value'], label='Validation')
ax.set_xlabel('Epoch')
ax.set_ylabel('Loss (MSE)')
# ax.set_yscale('log')
ax.set_title('Epoch loss (MSE) for run ' + runs[RUN])
plt.legend()
# Show the major grid lines with dark grey lines
plt.grid(b=True, which='major', color='#666666', linestyle='-')
# Show the minor grid lines with very faint and almost transparent grey lines
plt.minorticks_on()
plt.grid(b=True, which='minor', color='#999999', linestyle='-', alpha=0.2)
plt.show()
print(train)