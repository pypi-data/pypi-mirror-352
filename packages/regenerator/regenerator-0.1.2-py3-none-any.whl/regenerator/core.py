import threading
import queue


class Regenerator:
    """
    A Regenerator is a generator that can be iterated multiple times.

    Parameters
    ----------
    generator : generator
        A generator that will be duplicated.
    """

    def __init__(self, generator):
        """
        Initialize the Regenerator with a generator.

        Parameters
        ----------
        generator : generator
            A generator that will be duplicated.
        """

        self.generator = generator

    def __iter__(self):
        """
        Return an iterator for the Regenerator.

        Returns
        -------
        Regenerator
            A new instance of Regenerator that can be iterated over.
        """

        return self.copy()

    def __list__(self):
        """
        Convert the Regenerator to a list.

        Returns
        -------
        list
            A list containing all items produced by the Regenerator.
        """

        return list(self.copy())

    def copy(self):
        """
        Create a copy of the Regenerator's generator.

        Returns
        -------
        generator
            A new generator that is a duplicate of the original.
        """

        g1, g2 = duplicate(self.generator)
        self.generator = g1
        return g2


def duplicate(generator):
    """
    Duplicate a generator using threads and queues.

    Parameters
    ----------
    generator : generator
        The generator to be duplicated.

    Returns
    -------
    tuple
        A tuple containing two generators that yield the same items as the original generator.
    """

    q1 = queue.Queue()
    q2 = queue.Queue()

    class End:
        def __init__(self):
            pass

    end = End()

    def queue_to_generator(q):
        while True:
            item = q.get()
            if isinstance(item, End):
                break
            yield item

    def producer():
        for item in generator:
            q1.put(item)
            q2.put(item)
        q1.put(end)
        q2.put(end)

    threading.Thread(target=producer, daemon=True).start()
    return queue_to_generator(q1), queue_to_generator(q2)


if __name__ == "__main__":
    g0 = (i for i in range(5))
    g1, g2 = duplicate(g0)
    assert list(g1) == list(g2)
