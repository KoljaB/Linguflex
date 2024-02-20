import time


class AnimationHandler:
    _instance = None

    @classmethod
    def _Handler(self):
        """
        Returns the singleton instance of the AnimationHandler class.
        If the instance does not exist, it creates one.
        """
        if self._instance is None:
            self._instance = AnimationHandler._AnimationHandler()
        return self._instance

    class _AnimationHandler:
        def __init__(self):
            self.animations = []

        def add(self, animation, run=True):
            """
            Adds an animation to the list of animations.
            """
            self.animations.append(animation)

            if run:
                animation.run()

        def add_and_run(self, animation):
            """
            Adds an animation to the list of animations.
            """
            self.add(animation, True)

        def update(self):
            """
            Updates all the animations in the list.
            """
            for animation in self.animations:
                animation.calculate_value()

        def is_animation_running(self):
            """
            Returns True if any animation is running, False otherwise.
            """
            self.update()
            for animation in self.animations:
                if animation.start_time:
                    return True
            return False

        def get_value(self, animation):
            """
            Returns the current value of an animation.
            """
            return animation.current_value

        def remove_animation(self, animation):
            """
            Removes an animation from the list of animations.
            """
            self.animations.remove(animation)


class Animation():
    """
    A class that represents an animation.
    """

    @classmethod
    def Handler(self):
        """
        Returns the singleton instance of the AnimationHandler class.
        """
        return AnimationHandler._Handler()

    def __init__(
            self,
            start_value,
            end_value,
            duration_seconds=1,
            ease_in=None,
            ease_out=None,
            direction_to_end=True,
            name="no name"):
        """
        Initializes an instance of the Animation class.

        Args:
        start_value (float): The starting value of the animation.
        end_value (float): The ending value of the animation.
        duration_seconds (float): The duration of the animation in seconds.
          Default is 1 second.
        ease_in (bool): Determines if to use easing function for the beginning
          of the animation.
        ease_out (bool): Determines if to use easing function for the end
          of the animation.
        direction_to_end (bool): The direction of the animation. True if the
          animation is from start to end, False if it is from end to start.
          Default is True.
        name (str): The name of the animation. Default is "no name".
        """
        self.start_value = start_value
        self.end_value = end_value
        self.name = name
        self.duration_seconds = duration_seconds
        self.ease_in = ease_in
        self.ease_out = ease_out
        self.start_time = None

        self.current_value = start_value
        self.distance = end_value - start_value
        self.direction_to_end = direction_to_end

    def run_reverse(self):
        self.run(not self.direction_to_end)

    def run(self, direction_to_end=None):
        """
        Starts the animation.

        Args:
        direction_to_end (bool): The direction of the animation.
        True if the animation is from start to end,
        False if it is from end to start. Default is None.

        Returns:
        None
        """
        current_time = time.time()

        if direction_to_end is None:
            direction_to_end = self.direction_to_end

        if self.is_running():
            if self.direction_to_end != direction_to_end:
                elapsed_time = current_time - self.start_time
                percentage_of_duration = elapsed_time / self.duration_seconds
                inverse_percentage = 1 - percentage_of_duration
                self.start_time = (
                    current_time - self.duration_seconds * inverse_percentage
                )
                self.direction_to_end = direction_to_end
            self.calculate_value()
            return

        self.direction_to_end = direction_to_end
        self.start_time = current_time
        if self.direction_to_end:
            self.current_value = self.start_value
        else:
            self.current_value = self.end_value

    def is_start(self):
        return self.current_value == self.start_value

    def is_end(self):
        return self.current_value == self.end_value

    def is_running(self):
        """
        Returns True if the animation is running, False otherwise.

        Returns:
        bool: True if the animation is running, False otherwise.
        """
        return self.start_time and not self.is_start()

    def stop(self):
        """
        Stops the animation.

        Returns:
        None
        """
        self.start_time = None
        if self.direction_to_end:
            self.current_value = self.start_value
        else:
            self.current_value = self.end_value

    def _ease_in(self, t):
        """
        The easing function for the beginning of the animation.

        Args:
        t (float): The time value.

        Returns:
        float: The eased value.
        """
        return t*t*t

    def _ease_out(self, t):
        """
        The easing function for the end of the animation.

        Args:
        t (float): The time value.

        Returns:
        float: The eased value.
        """
        return (t-1)*(t-1)*(t-1) + 1

    def calculate_value(self):
        """
        Calculates the current value of the animation.

        Returns:
        float: The current value of the animation.
        """
        current_time = time.time()

        if not self.start_time:
            return self.current_value

        elapsed_time = current_time - self.start_time

        if elapsed_time > self.duration_seconds:
            if self.direction_to_end:
                self.current_value = self.end_value
            else:
                self.current_value = self.start_value
            return self.current_value

        t = elapsed_time / self.duration_seconds

        if not self.direction_to_end:
            t = 1 - t

        if self.ease_in and not self.ease_out:
            t = self._ease_in(t)
        elif self.ease_out and not self.ease_in:
            t = self._ease_out(t)
        elif self.ease_in and self.ease_out:
            if t < 0.5:
                t = self._ease_in(t*2)/2
            else:
                t = self._ease_out((t-0.5)*2)/2 + 0.5

        self.current_value = self.start_value + self.distance * t
        return self.current_value
