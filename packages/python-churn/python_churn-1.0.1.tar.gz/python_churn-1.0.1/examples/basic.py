#!/usr/bin/env python

"""Executes basic example."""

from pathlib import Path

import churn

context = {'numbers': 100, 'every_n': 5}
output_folder = Path('../runs/basic/run01')
template_dir = Path('basic')

churn.Configurator(
    context,
    output_folder,
    template_dir,
).render()

churn.run_chain(
    churn.Task(
        'pre_numbers',
        template_dir,
        output_folder,
        [Path('pre_numbers/numbers.txt')],
    )
)
churn.create_batch_chain(
    churn.Task(
        'nth_numbers',
        template_dir,
        output_folder,
        [Path('nth_numbers/numbers.txt')],
        [Path('pre_numbers/numbers.txt')],
    ),
    churn.Task(
        'count_lines',
        template_dir,
        output_folder,
        [Path('pre_numbers/numbers.txt')],
        [Path('count_lines/num_of_nums.txt')],
    ),
)
