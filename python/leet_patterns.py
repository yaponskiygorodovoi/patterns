# 1. DYNAMIC PROGRAMMING / FIBONACCI PATTERN
# Используем результаты двух предыдущих шагов, чтобы вычислить следующий.
# Не храним весь массив значений — только два предыдущих результата.
# Время: O(n), память: O(1)

class Solution(object):
    def climbStairs(self, n):

        if n == 1:
            return 1

        prev1 = 1
        prev2 = 2

        step = 3

        while step <= n:
            current = prev1 + prev2

            prev1 = prev2
            prev2 = current

            step += 1

        return prev2


print(Solution().climbStairs(5))


# ============================================================


# 2. STACK PATTERN
# Используем стек для проверки правильного порядка вложенных элементов.
# Открывающую скобку кладём в стек.
# Закрывающую сравниваем с последней открытой.
# Принцип: Last In — First Out (LIFO).
# Время: O(n), память: O(n)

class Solution(object):
    def isValid(self, s):
        stack = []

        pairs = {
            ')': '(',
            ']': '[',
            '}': '{'
        }

        for char in s:

            if char in '([{':
                stack.append(char)

            else:
                if not stack:
                    return False

                if stack[-1] != pairs[char]:
                    return False

                stack.pop()

        return len(stack) == 0


# ============================================================


# 3. SORT + MERGE INTERVALS PATTERN
# Сначала сортируем интервалы.
# Затем сравниваем текущий интервал с последним добавленным.
# Если интервалы пересекаются — объединяем их.
# Если нет — создаём новый интервал.
# Время: O(n log n), память: O(n)

class Solution(object):
    def merge(self, intervals):
        intervals.sort()

        merged = []

        for interval in intervals:

            if not merged:
                merged.append(interval)

            else:
                last = merged[-1]

                if interval[0] <= last[1]:
                    last[1] = max(last[1], interval[1])

                else:
                    merged.append(interval)

        return merged


# ============================================================


# 4. HASH MAP LOOKUP / COMPLEMENT PATTERN
# Для каждого числа вычисляем, какое число нам нужно до target.
# В словаре храним уже просмотренные числа и их индексы.
# Вместо второго вложенного цикла делаем быстрый поиск в словаре.
# Время: O(n), память: O(n)

nums = [2, 7, 11, 15]
target = 9

class Solution:
    def twoSum(self, nums, target):
        seen = {}

        for index, num in enumerate(nums):
            need = target - num

            if need in seen:
                return [seen[need], index]

            seen[num] = index


# ============================================================


# 5. HASH MAP GROUPING / GROUP BY KEY PATTERN
# Для каждого объекта вычисляем общий ключ группировки.
# Все элементы с одинаковым ключом складываем в одну группу словаря.
# Здесь анаграммы имеют одинаковый ключ после сортировки букв.
# Аналог GROUP BY в SQL.
# Время: примерно O(n * k log k), где k — длина слова.

class Solution:
    def groupAnagrams(self, strs):
        groups = {}

        for word in strs:
            key = "".join(sorted(word))

            if key not in groups:
                groups[key] = []

            groups[key].append(word)

        return list(groups.values())


# ============================================================


# 6. INDEX MARKING / ARRAY AS MEMORY PATTERN
# Используем сам массив как структуру памяти.
# Значение числа превращаем в индекс: value - 1.
# Отрицательное значение по этому индексу означает:
# "это число уже встречалось".
# Позволяет не использовать set или дополнительный словарь.
# Время: O(n), дополнительная память: O(1)

class Solution:
    def findDuplicates(self, nums):
        result = []

        for num in nums:
            index = abs(num) - 1

            if nums[index] < 0:
                result.append(abs(num))
            else:
                nums[index] = -nums[index]

        return result


# ============================================================


# 7. SLIDING WINDOW — MAXIMUM VALID WINDOW
# Правый указатель расширяет окно.
# Если условие нарушается (появился дубль),
# левый указатель сужает окно, пока оно снова не станет валидным.
# Используем для поиска максимального диапазона,
# удовлетворяющего условию.
# Время: O(n), память: O(k)

class Solution:
    def lengthOfLongestSubstring(self, s):
        chars = set()
        left = 0
        max_length = 0

        for right in range(len(s)):

            while s[right] in chars:
                chars.remove(s[left])
                left += 1

            chars.add(s[right])

            max_length = max(
                max_length,
                right - left + 1
            )

        return max_length


# ============================================================


# 8. SLIDING WINDOW — MINIMUM VALID WINDOW
# Правый указатель расширяет окно, пока не выполнится условие.
# Когда окно стало валидным, левый указатель начинает его сжимать.
# Так ищем минимальный диапазон, содержащий все нужные элементы.
#
# need     — сколько символов требуется
# window   — сколько символов сейчас внутри окна
# formed   — сколько требований полностью выполнено
# required — сколько требований всего
#
# Время: O(n), память: O(k)

class Solution:
    def minWindow(self, s, t):

        if not s or not t:
            return ""

        need = {}

        for char in t:
            need[char] = need.get(char, 0) + 1

        window = {}

        left = 0
        formed = 0
        required = len(need)

        min_length = float("inf")
        min_left = 0

        for right in range(len(s)):

            char = s[right]

            window[char] = window.get(char, 0) + 1

            if char in need and window[char] == need[char]:
                formed += 1

            while formed == required:

                current_length = right - left + 1

                if current_length < min_length:
                    min_length = current_length
                    min_left = left

                left_char = s[left]

                window[left_char] -= 1

                if (
                    left_char in need
                    and window[left_char] < need[left_char]
                ):
                    formed -= 1

                left += 1

        if min_length == float("inf"):
            return ""

        return s[min_left:min_left + min_length]