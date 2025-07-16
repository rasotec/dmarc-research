from collections import defaultdict
from io import StringIO
from statistics import mean, median, mode, stdev, variance
from typing import TextIO, Dict


def merge_dicts(dict1: Dict, dict2: Dict) -> defaultdict[str, int]:
    for key, value in dict2.items():
        assert type(value) == int
        if key in dict1:
            dict1[key] += value
        else:
            dict1[key] = value
    return dict1


class Counter:
    def __getitem__(self, item) -> Dict:
        pass

    def dumps(self, fp: TextIO) -> None:
        pass

    def dump(self) -> str:
        pass

    def announce(self, key) -> None:
        pass

    def merge(self, other) -> None:
        pass


class DataCounter(defaultdict, Counter):
    def __init__(self, title: str, description: str, header: str):
        super(DataCounter, self).__init__(int)
        self.reference_sum = 0
        self.title = title
        self.description = description
        self.headers = [header, 'Total count', 'Relative percentage']

    def __str__(self) -> str:
        return f"DataCounter: {self.title}"

    def merge(self, other: 'DataCounter') -> None:
        """
        Merge another DataCounter instance into this one.
        This method combines the data from both instances, ensuring that when _calculate()
        is called, the counts for each permutation will reflect the combined data.

        Args:
            other: Another DataCounter instance to merge with this one
        """
        # Ensure both instances have the same title, description, and order
        assert self.title == other.title, "Cannot merge DataCounter instances with different titles"
        assert self.description == other.description, "Cannot merge DataCounter instances with different descriptions"
        assert self.headers == other.headers, "Cannot merge DataCounter instances with different headers"

        # Merge the data
        for key, value in other.items():
            assert type(key) == int
            if key in self:
                # For existing keys, combine the integer values
                # This ensures that when _calculate() is called, the counts will be correct
                self[key] += value
            else:
                # For new keys, copy the default dict
                self[key] = value

    def dumps(self, fp: TextIO) -> None:
        if not self.reference_sum or self.reference_sum == 0:
            raise NotImplementedError

        # Sort dict by key
        data = dict(sorted(self.items(), key=lambda item: item[0]))

        # Compute sums and lengths for formatting
        data_sum = sum(data.values())
        data_value_len = len(f"{data_sum:,}")

        # Print the title as a Markdown heading
        fp.write(f"## {self.title}\n\n")

        # Print description
        fp.write(f"{self.description}\n\n")

        fp.write('-------\n\n')

        # Print the header row
        fp.write("| " + " | ".join(self.headers) + " |\n")
        # Print the separator row
        fp.write("|" + "|".join(["---"] * len(self.headers)) + "|\n")

        # Print each data row
        for key, count in data.items():
            percentage = (count / data_sum * 100) if data_sum else 0
            fp.write(
                f"| {key} "
                f"| {count:>{data_value_len},} "
                f"| {percentage:6.2f}% |\n"
            )

        # Print SUM row
        # (for the percentage, use data_sum / reference_sum * 100)
        sum_percentage = (data_sum / self.reference_sum * 100) if self.reference_sum else 0
        fp.write(
            f"| SUM "
            f"| {data_sum:>{data_value_len},} "
            f"| {sum_percentage:6.2f}% |\n"
        )

    def dump(self) -> str:
        assert self.reference_sum > 0, "Reference sum must be greater than zero"
        with StringIO() as fp:
            self.dumps(fp)
            return fp.getvalue()


class DataDistribution(defaultdict, Counter):
    def __init__(self, title: str, description: str):
        super(DataDistribution, self).__init__(int)
        self.title = title
        self.description = description

    def __copy__(self):
        return DataDistribution(self.title, self.description)

    def __str__(self) -> str:
        return f"DataDistribution: {self.title}"

    def _calculate(self):
        self.expanded_values = []
        for val, count in self.items():
            self.expanded_values.extend([val] * count)
        self.expanded_values.sort()
        self.total_count = len(self.expanded_values)
        self.mean = mean(self.expanded_values) if self.expanded_values else 0
        self.median = median(self.expanded_values) if self.expanded_values else 0
        self.stdev = stdev(self.expanded_values) if self.expanded_values else 0
        self.variance = variance(self.expanded_values) if self.expanded_values else 0
        self.mode = mode(self.expanded_values) if self.expanded_values else 0
        self.percentiles = self._calculate_percentiles()
        self.max_count = max(self.values())
        self.min_count = min(self.values())
        self.max_value = max(self.keys())
        self.min_value = min(self.keys())

    def _calculate_percentiles(self) -> dict:
        if not self.expanded_values:
            return {'low_1pct': 0, 'low_10pct': 0, 'high_1pct': 0, 'high_10pct': 0}

        def percentile(lst, pct):
            index = int(round(pct * (self.total_count - 1)))
            return lst[index]

        return {
            'low_1pct': percentile(self.expanded_values, 0.01),
            'low_10pct': percentile(self.expanded_values, 0.10),
            'high_10pct': percentile(self.expanded_values, 0.90),
            'high_1pct': percentile(self.expanded_values, 0.99),
        }

    def merge(self, other: 'DataDistribution') -> None:
        """
        Merge another DataDistribution instance into this one.
        This method combines the data from both instances, ensuring that when _calculate()
        is called, the counts for each permutation will reflect the combined data.

        Args:
            other: Another DataDistribution instance to merge with this one
        """
        # Ensure both instances have the same title, description, and order
        assert self.title == other.title, "Cannot merge DataPermutation instances with different titles"
        assert self.description == other.description, "Cannot merge DataPermutation instances with different descriptions"

        # Merge the data
        for key, value in other.items():
            assert type(key) == int
            if key in self:
                # For existing keys, combine the integer values
                # This ensures that when _calculate() is called, the counts will be correct
                self[key] += value
            else:
                # For new keys, copy the default dict
                self[key] = value

    def dumps(self, fp: TextIO) -> None:
        self._calculate()

        fp.write(f"## {self.title}\n\n")
        fp.write(f"{self.description}\n\n")
        fp.write('-------\n\n')

        fp.write("| Statistic | Value |\n")
        fp.write("|-----------|--------|\n")

        stats = [
            ("Count of data points", f"{self.total_count:,}"),
            ("Mean", f"{self.mean:.2f}"),
            ("Median", f"{self.median:.2f}"),
            ("Standard deviation", f"{self.stdev:.2f}"),
            ("Variance", f"{self.variance:.2f}"),
            ("Mode", f"{self.mode}"),
            ("1% Percentile", str(self.percentiles['low_1pct'])),
            ("10% Percentile", str(self.percentiles['low_10pct'])),
            ("90% Percentile", str(self.percentiles['high_10pct'])),
            ("99% Percentile", str(self.percentiles['high_1pct'])),
            ("Max Count", str(self.max_count)),
            ("Min Count", str(self.min_count)),
            ("Max Value", str(self.max_value)),
            ("Min Value", str(self.min_value))
        ]

        for stat, value in stats:
            fp.write(f"| {stat} | {value} |\n")

    def dump(self) -> str:
        output = StringIO()
        self.dumps(output)
        contents = output.getvalue()
        output.close()
        return contents


class DataPermutation(dict, Counter):
    def __init__(self, title: str, description: str, order: list[str] = None):
        super(DataPermutation, self).__init__()
        self.title = title
        self.description = description
        self.order = order

    def __copy__(self):
        return DataPermutation(self.title, self.description, self.order)

    def __str__(self) -> str:
        return f"DataPermutation: {self.title}"

    def announce(self, key) -> None:
        if key not in self:
            self[key] = defaultdict(bool)

    def merge(self, other: 'DataPermutation') -> None:
        """
        Merge another DataPermutation instance into this one.
        This method combines the data from both instances, ensuring that when _calculate()
        is called, the counts for each permutation will reflect the combined data.

        Args:
            other: Another DataPermutation instance to merge with this one
        """
        # Ensure both instances have the same title, description, and order
        if self.title != other.title or self.description != other.description:
            raise ValueError("Cannot merge DataPermutation instances with different titles or descriptions")

        if (self.order is not None and other.order is not None and self.order != other.order) or \
                (self.order is None and other.order is not None) or \
                (self.order is not None and other.order is None):
            raise ValueError("Cannot merge DataPermutation instances with different orders")

        # Merge the data
        for key, value in other.items():
            if key in self:
                # For existing keys, combine the boolean values
                # This ensures that when _calculate() is called, the counts will be correct
                for field, bool_value in value.items():
                    self[key][field] = self[key][field] or bool_value
            else:
                # For new keys, copy the default dict
                self[key] = value.copy()

    def _calculate(self):
        assert len(self) > 0

        if self.order is not None:
            self.fields = self.order
        else:
            fields = set()
            for value in self.values():
                fields.update(value.keys())
            self.fields = list(fields)

        if len(self.fields) == 2:
            self.counts = {}
            for t1 in ['T', 'F', '-']:
                for t2 in ['T', 'F', '-']:
                    self.counts[f"{t1}{t2}"] = 0
            del self.counts['--']
            for value in self.values():
                f1 = 'T' if value[self.fields[0]] else 'F'
                f2 = 'T' if value[self.fields[1]] else 'F'
                self.counts[f"{f1}-"] += 1
                self.counts[f"-{f2}"] += 1
                self.counts[f"{f1}{f2}"] += 1
        elif len(self.fields) == 3:
            self.counts = {}
            for t1 in ['T', 'F', '-']:
                for t2 in ['T', 'F', '-']:
                    for t3 in ['T', 'F', '-']:
                        self.counts[f"{t1}{t2}{t3}"] = 0
            del self.counts['---']
            for value in self.values():
                f1 = 'T' if value[self.fields[0]] else 'F'
                f2 = 'T' if value[self.fields[1]] else 'F'
                f3 = 'T' if value[self.fields[2]] else 'F'
                self.counts[f"{f1}--"] += 1
                self.counts[f"-{f2}-"] += 1
                self.counts[f"--{f3}"] += 1
                self.counts[f"{f1}{f2}-"] += 1
                self.counts[f"{f1}-{f3}"] += 1
                self.counts[f"-{f2}{f3}"] += 1
                self.counts[f"{f1}{f2}{f3}"] += 1
        elif len(self.fields) == 4:
            self.counts = {}
            for t1 in ['T', 'F', '-']:
                for t2 in ['T', 'F', '-']:
                    for t3 in ['T', 'F', '-']:
                        for t4 in ['T', 'F', '-']:
                            self.counts[f"{t1}{t2}{t3}{t4}"] = 0
            del self.counts['----']
            for value in self.values():
                f1 = 'T' if value[self.fields[0]] else 'F'
                f2 = 'T' if value[self.fields[1]] else 'F'
                f3 = 'T' if value[self.fields[2]] else 'F'
                f4 = 'T' if value[self.fields[3]] else 'F'
                self.counts[f"{f1}---"] += 1
                self.counts[f"-{f2}--"] += 1
                self.counts[f"--{f3}-"] += 1
                self.counts[f"---{f4}"] += 1
                self.counts[f"{f1}{f2}--"] += 1
                self.counts[f"{f1}-{f3}-"] += 1
                self.counts[f"{f1}--{f4}"] += 1
                self.counts[f"-{f2}{f3}-"] += 1
                self.counts[f"-{f2}-{f4}"] += 1
                self.counts[f"--{f3}{f4}"] += 1
                self.counts[f"{f1}{f2}{f3}-"] += 1
                self.counts[f"{f1}{f2}-{f4}"] += 1
                self.counts[f"{f1}-{f3}{f4}"] += 1
                self.counts[f"-{f2}{f3}{f4}"] += 1
                self.counts[f"{f1}{f2}{f3}{f4}"] += 1

        self.perms = sorted(self.counts.items(), key=lambda x: x[0], reverse=True)

    def dumps(self, fp: TextIO) -> None:
        self._calculate()

        fp.write(f"## {self.title}\n\n")
        fp.write(f"{self.description}\n\n")
        fp.write('-------\n\n')

        # Create the header row
        headers = self.fields + ['Count', 'Percentage']
        fp.write("| " + " | ".join(headers) + " |\n")
        fp.write("|" + "|".join(["---"] * len(headers)) + "|\n")

        # Calculate max width for count column
        max_count = max(self.counts.values())
        count_width = len(f"{max_count:,}")

        # Print each permutation
        for permutation, count in self.perms:
            row = []
            # Add boolean values
            row.extend(list(permutation.replace('T', '✓').replace('F', '✗')))
            # Add count and percentage
            percentage = (count / len(self) * 100) if len(self) else 0
            row.append(f"{count:>{count_width},}")
            row.append(f"{percentage:6.2f}%")
            fp.write("| " + " | ".join(row) + " |\n")

        # Print total row
        total_row = ["-"] * len(self.fields)
        total_row.append(f"{len(self):>{count_width},}")
        total_row.append(f"{100.00:6.2f}%")
        fp.write("| " + " | ".join(total_row) + " |\n")

    def dump(self) -> str:
        with StringIO() as fp:
            self.dumps(fp)
            return fp.getvalue()
