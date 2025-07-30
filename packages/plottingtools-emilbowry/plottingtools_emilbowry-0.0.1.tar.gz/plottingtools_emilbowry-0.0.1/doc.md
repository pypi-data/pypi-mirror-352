# Specification: Dynamic Plotly Display Interception for `.py` Scripts and Notebooks

## 1. Introduction and Objective

This document outlines the specification for a system designed to enable the existing `Plots` class, along with its subclasses such as `SimulatorPlots`, to render Plotly figures effectively in two distinct execution environments: Jupyter Notebooks and standard Python (`.py`) scripts. The `Plots` class currently relies on `IPython.display.display(fig)` and `plotly.graph_objects.Figure.show()` for figure rendering. It is attached for reference.

The core objectives are:

-   **In Jupyter Notebooks:** The `Plots` class must continue to function as it currently does, displaying figures inline using Plotly's native rich MIME type rendering capabilities.
-   **In `.py` scripts:** All calls to `IPython.display.display()` and `plotly.graph_objects.Figure.show()` (originating from within the `Plots` class, its subclasses, or user code interacting with their outputs) must be intercepted. The Plotly figure data (ideally as JSON, or as executable JavaScript if JSON is not directly available) will be extracted and re-routed for rendering in a separate desktop GUI window. This GUI window will be managed by `pywebview` and will receive data via a `multiprocessing.Queue`.

A primary constraint is to achieve this dual-environment compatibility without altering the public interface or existing internal display call patterns of the `Plots` class and its subclasses. This ensures backward compatibility and maintains ease of use for existing codebases that utilize the `Plots` ecosystem. The immediate focus of this specification is to detail a solution for which feasibility can be clearly demonstrated, particularly for the script-mode execution pathway. This document aims to be a single, updated, and comprehensive specification reflecting all agreed-upon requirements and design decisions.

The context for this task is the transition of `Plots` functionality from being exclusively operational within `.ipynb` environments to also supporting execution directly from `.py` script files.

## 2. Core Requirements and Constraints

### 2.1. `Plots` Class Integrity and Modification Rules

-   **No Modification of Public Interface:** The existing public methods (e.g., `updateLiveScatter`, `createGraph`, `graphVariational`), their signatures, and established usage patterns of the `Plots` class and its subclasses (e.g., `SimulatorPlots`) must remain entirely unaltered.
-   **Preservation of Internal Display Calls:** All `IPython.display.display(...)` and `plotly.graph_objects.Figure.show()` calls, whether they originate from within the `Plots` class, its subclasses, or user code invoking these classes, must be preserved in their current form. The solution must operate by intercepting these calls or their effects externally.
-   **API Contract Preservation:** Functions within the `Plots` class or its subclasses that are designed to return `fig` objects (e.g., `updateLiveScatter`, `createGraph`) must continue to do so to maintain compatibility with external workflows that may rely on these return values.
-   **Conditional Augmentation:** While the public interface must not change, the introduction of new _private_ methods or attributes to the `Plots` class or a helper mechanism (e.g., via a metaclass specifically for script-environment GUI management) is permissible. Such additions must not alter the existing public API or the observable behavior of the `Plots` class within notebook environments.

### 2.2. System Behavior and Modularity

-   **Environment-Specific Adaptation:** The solution must automatically and robustly detect the execution environment (notebook/IPython vs. standard `.py` script) and adapt its display mechanism accordingly.
-   **Modularity**: The interception logic and the GUI rendering components should be encapsulated, for instance, within a dedicated module (e.g., plot_interceptor.py). This design should be minimally invasive to the user's primary codebase. **Broad or uncontrolled monkey-patching of core Python, IPython, or Plotly functions (such as IPython.display.display itself or plotly.io.show) is to be avoided due to the high risk of unintended downstream consequences and library update brittleness. The system will rely on external interception of display events or interaction with well-defined internal components of display systems (such as the conditional modification of an IPython shell's DisplayPublisher instance as detailed in Section 4.3) where necessary.**

## 3. Environment Detection and Handling

-   **Robust Detection:** A reliable method, `isNotebookEnvironment()`, must be implemented to distinguish between notebook/IPython sessions and standard `.py` script execution. This will likely involve attempting to import and access `IPython.get_ipython()`. Unreliable checks (e.g., based on `__file__` presence) should be avoided.
-   **Notebook Environment Behavior:**
    -   If `isNotebookEnvironment()` returns true, the interception mechanism should effectively become a no-op, allowing Plotly's default rich display mechanisms within the notebook to function as they currently do, without interference.
    -   The `DisplayPublisher` monkey-patching approach (detailed in Section 4.3) should only be considered for notebook environments if very specific, fine-grained control beyond default behavior is absolutely necessary and can be implemented without disrupting normal notebook operation or the user experience.
-   **Script Environment Behavior:**
    -   If `isNotebookEnvironment()` returns false, the script-specific interception and GUI redirection logic must be activated.

## 4. Interception Strategies for `.py` Scripts

When running in a `.py` script environment, the system must intercept calls that would normally attempt to render Plotly figures inline or through other means not suitable for a non-notebook context.

### 4.1. Primary Strategy: Embedded IPython Kernel (`KernelManager`)

-   **Mechanism:** Utilize `jupyter_client.KernelManager` to start a lightweight, in-process IPython kernel. This approach is preferred over using `jupyter_client.BlockingKernelClient` directly for all interactions or a full `IPKernelApp` instance, due to better stability, fewer observed downstream effects, and a more lightweight footprint for this specific use case.
-   **Operation:**
    1.  Initialize and start the `KernelManager` and its associated client (`kc = km.client()`).
    2.  Start a separate thread (e.g., `iopub_listener`) dedicated to listening to the kernel's `iopub` channel. This listener will monitor for `display_data` or `update_display_data` messages.
    3.  Calls to `IPython.display.display()` and `fig.show()` (which often routes through `IPython.display.display()` internally when an IPython environment is detected or emulated) will generate messages on this `iopub` channel.
-   **Data Extraction:** Refer to Section 5.1.

### 4.2. Fallback/Complementary Strategy: `sys.stdout` Redirection & Parsing (`StdoutInterceptor`)

-   **Mechanism:** Implement a custom class (e.g., `StdoutInterceptor`) that can be used to temporarily replace `sys.stdout`. This class will inspect all data being written to the standard output stream.
-   **Rationale:**
    -   This can serve as a fallback if the `KernelManager` setup encounters issues or proves problematic in certain restricted environments.
    -   Crucially, it can capture output that the embedded kernel _itself_ might print to `stdout`, or output from `display()` calls if they fall back to string representations in a script context without a fully active display hook. This is important because the kernel's string representation of display messages (or direct `print(figure_object)` equivalents) might be more reliably captured from `stdout` than through direct IOPub message parsing in some edge cases, or if IOPub messages are unexpectedly malformed or not generated as expected.
    -   While clean kernel message interception via IOPub is the ideal, `stdout` parsing is a practical measure, especially considering the varied ways `display()` might behave or be shimmed in different script setups.
-   **Operation:**
    1.  The `StdoutInterceptor`'s `write()` method will receive strings intended for standard output.
    2.  It will parse these strings to identify and extract Plotly figure data.
-   **Data Extraction:** Refer to Section 5.2.

### 4.3. Alternative (Conditional) Strategy: `DisplayPublisher` Monkey Patching

-   **Mechanism:** If an `InteractiveShell` instance is available and detected (e.g., via `InteractiveShell.instance()`), its `display_pub` attribute (an instance of `IPython.core.displaypub.DisplayPublisher`) can be replaced with a custom subclass.
-   **Operation:** The `publish` method of this custom `DisplayPublisher` subclass would intercept display calls. It can inspect the `data` dictionary (the MIME bundle) for Plotly-specific MIME types and reroute them as needed before or instead of the standard publication.
-   **Use Case:** This strategy is primarily relevant if fine-grained control over the display publication mechanism is needed within an active IPython session. It could potentially be used even in a notebook for specific overrides (though the primary goal is to preserve default notebook behavior). It is less suitable as a primary mechanism for generic `.py` scripts if the aim is to avoid dependencies on a full IPython shell setup, but it could be conditionally activated if `get_ipython()` returns a valid shell instance. This provides a more nuanced approach than a blanket prohibition on monkey patching, allowing it where it is a natural extension of IPython's own mechanisms.

## 5. Data Extraction, Parsing, and Filtering (for `.py` Scripts)

Once a display event is intercepted in a `.py` script environment, the Plotly figure data must be meticulously extracted and prepared for the GUI.

### 5.1. From IOPub Messages (`KernelManager` Strategy)

-   **Preferred Format:** Extract data associated with the `application/vnd.plotly.v1+json` MIME type from the `display_data` or `update_display_data` message. This format directly provides the Plotly figure as a JSON-compatible Python dictionary (e.g., `{'data': [...], 'layout': {...}}`).
-   **Fallback Format:** If the `application/vnd.plotly.v1+json` MIME type is not present in a `display_data` message, the system should parse the `text/html` content within the message. The parser will search for `<script>` tags containing JavaScript calls like `Plotly.newPlot(...)` or `Plotly.react(...)`.

### 5.2. From `sys.stdout` Strings (`StdoutInterceptor` Strategy)

The `StdoutInterceptor` must be capable of parsing different string formats that might represent Plotly figures:

-   **Output from `IPython.display.display(fig)` (String Representation of Figure Object):**
    -   This typically results in a string written to `stdout` resembling: `Figure({'data': [{'type': 'scatter', ...}], 'layout': {...}})`
    -   This string should be parsed by stripping the `Figure(` prefix and `)` suffix, and then processing the remaining content (e.g., using `ast.literal_eval`) into a Python dictionary.
-   **Output from `fig.show()` (String Representation of MIME Bundle):**
    -   When an active kernel (even embedded) routes `fig.show()` output to `stdout`, it may print a string representation of a Python dictionary, which is effectively a MIME bundle: `{'text/html': '<script>... Plotly.newPlot(...); ...</script>', 'application/vnd.plotly.v1+json': {'data': [...], 'layout': {...}}}`
    -   The parsing logic for this case must:
        1.  Attempt to parse this outer dictionary string (e.g., using `ast.literal_eval` if necessary, after appropriate cleaning).
        2.  Prioritize extracting the content of the `'application/vnd.plotly.v1+json'` key if present. This yields the direct Plotly JSON.
        3.  If `'application/vnd.plotly.v1+json'` is not available, or as a fallback, extract and parse the relevant JavaScript calls (`Plotly.newPlot(...)`, `Plotly.react(...)`) from the content of the `'text/html'` key.

### 5.3. Noise Filtering for JavaScript

-   When extracting JavaScript from `text/html` content (either from IOPub messages or `stdout` strings), the parser must actively filter out irrelevant or example JavaScript code.
-   A known example that requires filtering is the Mapbox token example often included by Plotly: `Plotly.newPlot(gd, data, layout, { mapboxAccessToken: 'my-access-token' });`
-   The objective is to isolate and extract only the specific `Plotly.newPlot(...)` or `Plotly.react(...)` call that is responsible for rendering the actual figure data.

## 6. GUI Rendering Layer (`pywebview`)

For `.py` scripts, intercepted plot data will be rendered in a separate desktop GUI window managed by `pywebview`.

-   **Technology:** `pywebview` will be used to create and manage the native desktop window.
-   **Communication:** A `multiprocessing.Queue` (e.g., named `gui_command_queue`) will facilitate robust, inter-process communication from the main Python script (where the `Plots` class is used and interception occurs) to a separate GUI process that manages the `pywebview` window.
-   **GUI Process:**
    -   A dedicated target function (e.g., `gui_process_target`) will run in a separate `multiprocessing.Process`.
    -   This function will instantiate a GUI manager class (e.g., `WindowDisplay`). This class will be responsible for the `pywebview` window's lifecycle, loading the initial HTML, and processing commands received from the `gui_command_queue`.
    -   The `WindowDisplay` class will load an HTML template. This template must include the Plotly.js library (e.g., via `<script src='https://cdn.plot.ly/plotly-latest.min.js'></script>`) and a designated `div` element (e.g., `<div id='graph_div'></div>`) where plots will be rendered.
-   **Rendering Commands (Received by GUI process via Queue):**
    -   **Type `PLOTLY_FIG_JSON`:**
        -   Payload: A Python dictionary representing the Plotly figure, typically `{'data': [...], 'layout': {...}}`.
        -   Action: The GUI process will use JavaScript like `Plotly.react('graph_div', payload.data, payload.layout);` (or `Plotly.newPlot` for the initial plot) to render/update the figure in the `webview`.
    -   **Type `DISPLAY_JS`:**
        -   Payload: A raw JavaScript string (e.g., `'Plotly.newPlot("graph_div", ...);'`).
        -   Action: The GUI process will use `webview_window.evaluate_js(payload);` to execute the JavaScript directly in the `webview` context.
-   **Sending Functions (Callable from main script/interceptor to GUI queue):**
    -   `sendPlotlyFigToGuiDict(figure_dict)`: This function will take a Python dictionary (the parsed Plotly figure JSON) and put a command of type `PLOTLY_FIG_JSON` with the `figure_dict` as payload onto the `gui_command_queue`.
    -   `sendRawJsToGui(js_string)`: This function will take a raw JavaScript string and put a command of type `DISPLAY_JS` with the `js_string` as payload onto the `gui_command_queue`.
-   **GUI Lifecycle Management:**
    -   A function, such as `launchViewerIfNeeded()`, will be responsible for ensuring that the GUI process and its associated `pywebview` window are started only once, and only when the first plot needs to be displayed in a script environment.
    -   A mechanism to signal the GUI process to terminate cleanly (e.g., a special 'DESTROY' command placed on the `gui_command_queue`) must be implemented to allow for proper shutdown and resource release.

## 7. `Plots` Class Specific Behaviors & Handling

The interception mechanism must be robust enough to correctly handle display calls originating from various methods within the `Plots` class and its subclasses, based on their known implementation patterns.

-   **`Plots.updateLiveScatter(fig, y, x)`:**
    -   If the input `fig` is not already a `go.FigureWidget`, it is converted to one, and then `IPython.display.display(fig)` is called internally. This `display()` call must be intercepted in script mode, and the figure data must be extracted and forwarded to the `pywebview` GUI.
    -   Subsequent updates to the figure within this method typically use `fig.batch_update()`. For an already displayed `FigureWidget`, this action should trigger `update_display_data` messages on the IOPub channel (if the `KernelManager` strategy is active). These messages must be captured and their data efficiently forwarded to the GUI to reflect the live updates.
-   **`Plots.createGraph(graph_parameters, display_figure=True, ...)`:**
    -   If `graph_parameters.get('fig_type') == 'Widget'` (as used, for example, by `Plots.graphVariational` which often wraps a `go.FigureWidget` and interactive controls like sliders in an `ipywidgets.VBox` container):
        -   `Plots.createGraph` will call `IPython.display.display(container)`.
        -   The interception logic needs to handle this `display(container)` call. Ideally, it should attempt to extract the Plotly `FigureWidget`'s data from the container's display representation if possible. Alternatively, or additionally, it must listen for subsequent `display_data` or `update_display_data` messages specifically associated with the `FigureWidget` itself once it's rendered within the container.
    -   Otherwise (for non-widget figure types, e.g., standard `go.Figure`):
        -   `Plots.createGraph` will call `fig.show()`. This call must be intercepted, and the figure data extracted and sent to the `pywebview` GUI.
-   **`Plots.graphVariational(...)`:**
    -   This method prepares parameters for `Plots.createGraph` with the intention of displaying a `go.FigureWidget` often embedded within an `ipywidgets.VBox` container that includes interactive sliders (e.g., for alpha and beta parameters).
    -   The interaction callbacks for these sliders (e.g., the `refresh` function within `graphVariational`) typically use `fig.batch_update()` to modify the plot. For an already displayed `FigureWidget`, these updates are expected to emit `update_display_data` IOPub messages. These messages are critical for interactivity and must be captured and efficiently relayed to the `pywebview` GUI to reflect the changes driven by slider manipulation.
-   **General Display Calls to Handle:** The system must be prepared to intercept and correctly process various forms of display invocation:
    -   `fig.show()` (where `fig` is a `plotly.graph_objects.Figure` or `FigureWidget`, called by `Plots` or user code).
    -   `IPython.display.display(go.Figure_object)` (called by `Plots` or user code).
    -   `IPython.display.display(go.FigureWidget_object)` (called by `Plots` or user code).
    -   `IPython.display.display(ipywidgets_container_object)` when that container wraps a Plotly figure or widget (a pattern used within `Plots`, especially for interactive scenarios).

## 8. Performance Considerations

-   **Minimal Overhead in Scripts:** This is a critical requirement, particularly for:
    -   Dynamic plot updates occurring in loops (e.g., as in `Plots.updateLiveScatter`).
    -   Interactive widget scenarios, such as `Plots.graphVariational`, where slider movements trigger frequent plot updates. The system must maintain responsiveness.
-   **Kernel Startup Cost:** An `O(1)` (constant time) cost for the `KernelManager` spin-up at the beginning of a `.py` script execution is considered acceptable.
-   **Downstream Processing Efficiency:** The processing of intercepted messages – including parsing data, filtering, and placing it onto the GUI command queue – must be highly efficient to maintain GUI responsiveness, especially for `update_display_data` messages originating from widget interactions which can be frequent.

## 9. Advanced Integration Ideas (Conditional Consideration)

-   **Metaclass for Local GUI Management in Scripts:**
    -   Consider the use of a Python metaclass that, when operating in a `.py` script environment, could augment the `Plots` class (or a dedicated helper class associated with `Plots` instances).
    -   This augmentation could potentially enable a `Plots` instance (or its helper) to directly manage its own `pywebview` window instance if deemed beneficial.
    -   **Potential Benefits:** This could lead to better encapsulation of GUI lifecycle management, potentially simpler state synchronization if the `Plots` object itself becomes aware of its GUI counterpart, and perhaps more straightforward resource cleanup (e.g., garbage collection of the window alongside the plot object it represents).
    -   **Strict Constraint:** Any such implementation must be achieved without altering the public API of the `Plots` class or its observable behavior in Jupyter Notebook environments. This remains an idea for potential future refinement if the core mechanism proves successful and such encapsulation offers significant advantages.

## 10. Key Challenges

The successful implementation of this system will need to address several key challenges:

-   **Reliable Environment Detection:** Ensuring the system accurately and consistently identifies whether it's running in a notebook or a script to activate the correct mode.
-   **Minimally Invasive Hooking:** Intercepting `IPython.display.display` and `fig.show()` calls without breaking their normal functionality in notebooks or requiring modifications to the `Plots` class source code.
-   **Robust Parsing:** Developing resilient parsing logic to handle the various output formats (Plotly JSON directly from IOPub, `Figure({...})` string representations, HTML/JS from MIME bundles, string representations of MIME bundles themselves) and accurately extracting the necessary figure data while effectively filtering out noise.
-   **Kernel Interaction Management:** Balancing the robustness of kernel-based message capture (using `KernelManager`) with the potential need for `sys.stdout` parsing as a fallback or complement, especially if the embedded kernel itself contributes to `stdout` noise or if display mechanisms bypass IOPub under certain conditions.
-   **Lifecycle Management:** Correctly starting, managing, and tearing down the embedded kernel (if used with `KernelManager`) and the separate `pywebview` GUI process, ensuring no orphaned processes or resource leaks.
-   **Concurrency:** Properly managing concurrent operations, including the `iopub_listener` thread (for `KernelManager`) and the separate `multiprocessing.Process` for the GUI, ensuring thread-safe data exchange via the queue.
-   **`IPython.display.display` Availability/Shimming:** Ensuring that `IPython.display.display` is available or appropriately shimmed in the script context such that its calls can be reliably caught by one of the chosen interception strategies. This might involve an initial import script that sets up the interception environment before the user's `Plots`-using code runs, or careful handling of how `IPython` itself behaves when imported in a non-notebook script.

## 11. Development Approach & Conventions

### 11.1. Debugging Convention (Exception-Based)

To facilitate effective debugging during development, especially when `stdout` might be cluttered by kernel events, intercepted data, or other outputs, a specific convention will be used for inspecting successfully intercepted and processed data.

-   **Designation:** This exception-based mechanism is the primary method for _debugging_ the content of intercepted data.
-   **Rationale:** It provides a reliable way to halt execution at a point where data has been processed, allowing for inspection via a debugger. This avoids an over-reliance on `print` statements to `stdout` for debugging purposes, which can become unmanageable.
-   **Mechanism:** When a significant piece of data is successfully intercepted and processed (e.g., a parsed figure dictionary intended for the GUI, or a raw JavaScript string extracted for execution), an exception (e.g., a custom `DebugInterceptException` or a standard `RuntimeError`) should be raised. The exception message or arguments should contain the processed data.
-   **Usage:** Developers can set breakpoints on this specific exception type. When the exception is hit, the debugger will pause execution, allowing the developer to inspect the contents of the exception (and thus the intercepted data) before stepping past or continuing execution.
-   **Critical Rule for Propagation:** Any `try...except` block that might catch this debugging exception (e.g., a general `except Exception:`) _must_ re-raise it or allow it to propagate. This ensures that the exception reaches a point where the debugger can intercept it as intended, rather than being silently swallowed.
-   **Clear Distinction:** This debugging technique is distinct from general informational logging and from the `StdoutInterceptor`'s primary role, which is to capture data for actual display rendering in script mode, not for debugging inspection.

### 11.2. Code Style Conventions

Adherence to the following code style conventions is required for any code developed or proposed as part of this system, including prototypes and feasibility tests:

-   **Naming Convention:**
    -   All **variable names** must use `snake_case` (e.g., `figure_data`, `gui_command_queue`).
    -   All **function and method names** must use `camelCase` (e.g., `sendPlotlyFigToGuiDict`, `processIopubMessage`).
    -   All **class and type names** must use `PascalCase` (e.g., `WindowDisplay`, `StdoutInterceptor`, `DebugInterceptException`).
-   **Nesting:**
    -   A **maximum of 3 levels** of nested statements (e.g., loops, conditionals) is permitted within any single function or method body.
    -   **Aim for 1 level of nesting where possible.** Logic requiring more than 1-2 levels of nesting often indicates that a portion of it should be extracted into a separate, self-contained function or method to improve clarity and maintainability.
    -   **Rationale for Nesting Limits:** This promotes readability and helps ensure that a single function or method is responsible for a single, well-defined process or concern.
-   **Modularity and Separation of Concerns:** These are non-negotiable principles. Code should be organized into logical modules, classes, and functions, each with a clear and distinct responsibility.
-   **Generalization and Single Responsibility:** Functions and methods should be generalized wherever practical to promote reusability and reduce redundancy. Each function/method should ideally address a single concern. The design of `Plots.createGraph` within the existing `Plots` class serves as a good example of a generalized function.
-   **Application to Feasibility Tests:** These conventions should be applied even during the initial feasibility testing and prototyping phases to ensure consistency and lay a good foundation for any subsequent development.

## 12. Path Forward / Next Steps (Feasibility Focus)

The immediate goal is to demonstrate the feasibility of the approach outlined in this specification. The following steps are proposed:

1.  **Develop `isNotebookEnvironment()` function:** Implement and test a robust environment detection utility.
2.  **Implement Core Interception Logic (e.g., in `plot_interceptor.py`):**
    -   If `isNotebookEnvironment()` is true, this module should ensure that default notebook behavior is preserved by effectively doing nothing that interferes with Plotly's native rendering.
    -   If false (indicating a script environment):
        -   Initialize GUI management mechanisms (e.g., prepare for `launchViewerIfNeeded()`).
        -   **Primary Attempt: `KernelManager`-based interception.**
            -   Set up the `KernelManager`, its client, and the `iopub_listener` thread.
            -   The listener should parse `display_data` and `update_display_data` messages, prioritizing `application/vnd.plotly.v1+json` and falling back to `text/html` if necessary.
            -   Implement robust filtering for JavaScript extracted from HTML content (as per Section 5.3).
            -   Route extracted data to the GUI queue using `sendPlotlyFigToGuiDict` or `sendRawJsToGui`.
        -   **Fallback/Complementary: `StdoutInterceptor`-based interception.**
            -   Implement the `StdoutInterceptor` class.
            -   Ensure its parsing logic for `Figure({...})` strings and stringified MIME bundle dictionaries (potentially from `fig.show()` via kernel stdout) is as robust as possible, including the JavaScript noise filtering.
            -   Route extracted data similarly to the GUI queue.
        -   **Address `IPython.display.display` availability/interception:** Determine and document the precise mechanism by which `IPython.display.display` calls are made available or shimmed in the script context to ensure they are reliably caught by one of the interception strategies. This might involve an initial setup script or specific import patterns.
3.  **Develop/Refine GUI Management Module:**
    -   Implement `WindowDisplay`, `gui_process_target`, `launchViewerIfNeeded`, `sendPlotlyFigToGuiDict`, and `sendRawJsToGui` based on the structures defined in this specification and drawing from successful prototypes.
    -   Ensure `sendPlotlyFigToGuiDict` can correctly handle Python dictionaries derived from `ast.literal_eval` of `Figure({...})` strings as well as those directly obtained from `application/vnd.plotly.v1+json` bundles.
4.  **Testing:**
    -   Thoroughly test the complete solution using the provided `Plots` class (and `SimulatorPlots` if specific interactions differ) and established example usage patterns (e.g., MREs from Appendix A.5, `demo_executionCycle`, `test_displayFig`, etc.) in both script and notebook environments.
    -   Verify that all specified types of display calls (`IPython.display.display(fig_object)`, `fig.show()`, `IPython.display.display(widget_object)`, `IPython.display.display(container_object)`) are correctly handled according to the environment.
    -   Pay close attention to the behavior, responsiveness, and performance of interactive plots, particularly `Plots.graphVariational` with its slider-driven updates.
5.  **Adherence to Conventions:** Ensure that all implemented code strictly follows the code style and structural conventions outlined in Section 11.2.

The ultimate aim for this initial phase is to produce a solution that can be transparently activated (e.g., via a single import statement like `import enhanced_plotly_display_handler` at the beginning of a user's script). This would allow existing code that uses the `Plots` class to "just work" correctly and display figures appropriately in both Jupyter Notebook and standard Python script environments without requiring any modification to the user's `Plots`-related code.

## 13. Appendix (Reference Material)

This section will contain relevant code snippets, class definitions, and data examples for reference during implementation and testing. (Note: Code blocks are omitted in this draft as requested and will be filled in separately).

-   **A.1. `Plots` Class and `SimulatorPlots` Subclass Implementation:**
    See Attached File

-   **A.2. Example `StdoutInterceptor` and `StdoutRedirector` Class Structure:**

```python
import sys
# from .debug_utils import DebugInterceptException # Example custom exception

class StdoutInterceptor:
	def __init__(self, original_stdout, send_plotly_fig_dict_func, send_raw_js_func):
		self.original_stdout = original_stdout
		self.send_plotly_fig_dict = send_plotly_fig_dict_func
		self.send_raw_js = send_raw_js_func

	def write(self, text_to_write):
		self.original_stdout.write(text_to_write) # Pass through to actual stdout

		stripped_text = text_to_write.strip()
		if stripped_text.startswith('Figure({') and stripped_text.endswith('})'):
			try:
				import ast
				figure_str_content = stripped_text[len('Figure('):-1]
				figure_dict = ast.literal_eval(figure_str_content)
				if isinstance(figure_dict, dict) and 'data' in figure_dict:
					self.send_plotly_fig_dict(figure_dict)
					# raise DebugInterceptException(f'StdoutInterceptor: Processed Figure: {figure_dict}')
					return # Successfully processed
			except Exception as e:
				# self.original_stdout.write(f'StdoutInterceptor: Error parsing Figure string: {e}\n')
				pass # Fall through to other checks or ignore

		if 'Plotly.newPlot(' in stripped_text or 'Plotly.react(' in stripped_text:
			try:
				import re
				if 'mapboxAccessToken' in stripped_text and 'Plotly.newPlot(gd, data, layout, { mapboxAccessToken:' in stripped_text:
					return

				match = re.search(r'(Plotly\.(?:newPlot|react)\s*\(.*?\);)', stripped_text, re.DOTALL)
				if match:
					js_command = match.group(1)
					self.send_raw_js(js_command)
					# raise DebugInterceptException(f'StdoutInterceptor: Processed JS: {js_command}')
			except Exception as e:
				# self.original_stdout.write(f'StdoutInterceptor: Error parsing/extracting JS: {e}\n')
				pass
	def flush(self):
		self.original_stdout.flush()

class StdoutLogger:
    def __init__(self, logfile="stdout_log.txt"):
        self.logfile = logfile
        self._original_stdout = sys.stdout

    def write(self, s):
        with open(self.logfile, "a") as f:
            f.write(s)
        self._original_stdout.write(s)

    def flush(self):
        self._original_stdout.flush()

```

-   **A.3. Example `WindowDisplay` Class and `gui_process_target` Function Structure for `pywebview`:**

````python
```python
import json
import threading
import queue
import webview
import multiprocessing
import plotly.graph_objects as go
import sys
import time
from IPython.display import display


# --- Stdout Logger ---
class StdoutLogger:
    def __init__(self, logfile="stdout_log.txt"):
        self.logfile = logfile
        self._original_stdout = sys.stdout

    def write(self, s):
        with open(self.logfile, "a") as f:
            f.write(s)
        self._original_stdout.write(s)

    def flush(self):
        self._original_stdout.flush()


sys.stdout = StdoutLogger()



def extract_and_run_js_from_html(html_snippet):
    import re

    match = re.search(r"<script[^>]*>(.*?)</script>", html_snippet, re.DOTALL)
    if match:
        js_code = match.group(1)
        sendRawJsToGui(js_code)


# --- GUI Renderer ---
class WindowDisplay:
    HTML_TEMPLATE = """
    <html><head><script src=\"https://cdn.plot.ly/plotly-latest.min.js\"></script></head>
    <body><div id=\"graph_div\"></div></body></html>
    """

    def __init__(self, command_queue):
        self.command_queue = command_queue
        self.webview_window = None
        self._window_ready_event = threading.Event()

    def _on_webview_html_loaded(self):
        self._window_ready_event.set()

    def _process_commands(self):
        if not self._window_ready_event.wait(timeout=15):
            if self.webview_window:
                self.webview_window.destroy()
            return

        while True:
            try:
                command_data = self.command_queue.get(timeout=1.0)
                if command_data is None:
                    break

                cmd_type = command_data.get("type")
                payload = command_data.get("payload")

                if cmd_type == "PLOTLY_FIG_JSON":
                    if self.webview_window:
                        js_cmd = f"Plotly.react('graph_div', {json.dumps(payload['data'])}, {json.dumps(payload['layout'])});"
                        self.webview_window.evaluate_js(js_cmd)
                elif cmd_type == "DISPLAY_JS":
                    if self.webview_window:
                        self.webview_window.evaluate_js(payload)
                elif cmd_type == "DESTROY":
                    if self.webview_window:
                        self.webview_window.destroy()
                    break

            except queue.Empty:
                if not (self.webview_window and self.webview_window.gui):
                    break
                continue

    def run(self):
        gui_engine = "qt"
        threading.Thread(target=self._process_commands, daemon=True).start()

        self.webview_window = webview.create_window(
            "Plotly Viewer", html=self.HTML_TEMPLATE, width=800, height=600
        )
        self.webview_window.events.loaded += self._on_webview_html_loaded

        webview.start(gui=gui_engine, debug=False)
        self.command_queue.put(None)


def gui_process_target(command_queue):
    WindowDisplay(command_queue).run()


_gui_command_queue = multiprocessing.Queue()
_gui_process = multiprocessing.Process(
    target=gui_process_target, args=(_gui_command_queue,), daemon=True
)
_gui_started = False


def launchViewerIfNeeded():
    global _gui_started
    if not _gui_started:
        _gui_process.start()
        _gui_started = True


def sendPlotlyFigToGui(fig):
    if hasattr(fig, "to_plotly_json"):
        fig_json = fig.to_plotly_json()
        command = {"type": "PLOTLY_FIG_JSON", "payload": fig_json}
        _gui_command_queue.put(command)


def sendRawJsToGui(js_code):
    _gui_command_queue.put({"type": "DISPLAY_JS", "payload": js_code})


# --- Simplified Demo Class ---
class Plots:

    @staticmethod
    def scatter(x, y):
        return go.Figure(go.Scatter(x=x, y=y, mode="lines+markers"))

    @classmethod
    def show_scatter(cls, x, y):
        fig = cls.scatter(x, y)
        # sendPlotlyFigToGui(fig)
        display(fig)
        return fig

    @classmethod
    def updateLiveScatter(cls, fig, x_new, y_new):
        if not isinstance(fig, go.Figure):
            fig = go.Figure(fig)
        xs = (
            [*fig.data[0].x, *x_new]
            if isinstance(x_new, (list, tuple))
            else [*fig.data[0].x, x_new]
        )
        ys = (
            [*fig.data[0].y, *y_new]
            if isinstance(y_new, (list, tuple))
            else [*fig.data[0].y, y_new]
        )
        fig.data[0].x = xs
        fig.data[0].y = ys
        # sendPlotlyFigToGui(fig)
        fig.show()
        return fig


# --- Runtime Entry Point for Script Execution ---
if __name__ == "__main__":
    import numpy as np
    from jupyter_client import KernelManager

    def launch_embedded_kernel_and_listen():
        try:
            km = KernelManager()
            km.start_kernel()
            kc = km.client()
            kc.start_channels()

            def iopub_listener():
                while True:
                    try:
                        msg = kc.get_iopub_msg(timeout=1)
                        print("Received message:", msg)
                        if msg.get("msg_type") in (
                            "display_data",
                            "update_display_data",
                        ):
                            content = msg.get("content", {})
                            data = content.get("data", {})
                            if "text/html" in data:
                                extract_and_run_js_from_html(data["text/html"])

                    except Exception as e:
                        print("Non-critical exception in IOPub listener:", e)
                        continue

            threading.Thread(target=iopub_listener, daemon=True).start()
        except Exception as e:
            print("Embedded kernel listener setup failed:", e)

    launch_embedded_kernel_and_listen()
    launchViewerIfNeeded()

    x_data = []
    y_data = []

    # fig = Plots.show_scatter(x_data, y_data)
    i = 1
    # for i in range(100):
    fig = go.Figure(go.Scatter(x=[i], y=[np.sin(i / 10)], mode="lines+markers"))
    fig = Plots.updateLiveScatter(fig, i, np.sin(i / 10))
    # for i in range(100):
    #     fig = Plots.updateLiveScatter(fig, i, np.sin(i / 10))
    #     time.sleep(0.05)

````

-   **A.4. Data Format Examples Captured from Display Events:**
    -   \*\*`IPython.display.display(fig)` output to `stdout` (as string representation of Figure

```
		Figure({
			'data': [{'type': 'scatter', ...}],
			'layout': {...}
		})
```

    -**`fig.show()` output to `stdout` (MIME bundle as string, when kernel is active):**
    	This example shows a string representation of a Python dictionary. The `'text/html'` part can contain multiple JavaScript snippets, including examples that need to be filtered out.

```
		# String captured from stdout, representing a dict:
		'''
		{'text/html': '		<script type='text/javascript'>\\n		window.PlotlyConfig = {MathJaxConfig: \\'local\\'};\\n
		... [OTHER HTML AND JS] ...
		For example:','Plotly.newPlot(gd, data, layout, { mapboxAccessToken: \\'my-access-token\\' });','More info here: https://www.mapbox.com/help/define-access-token/'
		... [OTHER HTML AND JS] ...
		Plotly.newPlot(						'85aa1ee4-f4d3-406b-9c1b-077cc6f8ddd7',						[{'mode':'lines+markers','x':[1],'y':[0.099...],'type':'scatter'}],						{'template':{...}});
		... [END OF SCRIPT AND HTML] ...
		</script>',
		'application/vnd.plotly.v1+json': {'data': [{'mode': 'lines+markers', 'x': [1], 'y': [0.099...], 'type': 'scatter'}], 'layout': {'template': {...}}}
		}
		'''
		# Desired JS to extract from text/html (after filtering Mapbox example):
		# 'Plotly.newPlot('85aa1ee4-f4d3-406b-9c1b-077cc6f8ddd7', [{'mode':'lines+markers',...}], {'template':{...}});'
		# Preferred data to extract if available:
		# The content of 'application/vnd.plotly.v1+json'
```

    -**`application/vnd.plotly.v1+json` (from IOPub or parsed bundle):**
    	This is the ideal Python dictionary structure to obtain.

```python
		{'data': [{'type': 'scatter', ...}], 'layout': {...}}
```

-   **A.5. Prototype Stratergies**

## 5.1 Prototype Stratergy: Live Plotting - Working

```python
import threading
import queue
import webview
import multiprocessing
import plotly.graph_objects as go
import sys
import time
from IPython.display import display



# --- GUI Renderer ---
class WindowDisplay:
    HTML_TEMPLATE = """
    <html><head><script src=\"https://cdn.plot.ly/plotly-latest.min.js\"></script></head>
    <body><div id=\"graph_div\"></div></body></html>
    """

    def __init__(self, command_queue):
        self.command_queue = command_queue
        self.webview_window = None
        self._window_ready_event = threading.Event()

    def _on_webview_html_loaded(self):
        self._window_ready_event.set()

    def _process_commands(self):
        if not self._window_ready_event.wait(timeout=15):
            if self.webview_window:
                self.webview_window.destroy()
            return

        while True:
            try:
                command_data = self.command_queue.get(timeout=1.0)
                if command_data is None:
                    break

                cmd_type = command_data.get("type")
                payload = command_data.get("payload")

                if cmd_type == "PLOTLY_FIG_JSON":
                    if self.webview_window:
                        js_cmd = f"Plotly.react('graph_div', {json.dumps(payload['data'])}, {json.dumps(payload['layout'])});"
                        self.webview_window.evaluate_js(js_cmd)
                elif cmd_type == "DESTROY":
                    if self.webview_window:
                        self.webview_window.destroy()
                    break

            except queue.Empty:
                if not (self.webview_window and self.webview_window.gui):
                    break
                continue

    def run(self):
        gui_engine = "cocoa" if sys.platform == "darwin" else None
        threading.Thread(target=self._process_commands, daemon=True).start()

        self.webview_window = webview.create_window(
            "Plotly Viewer", html=self.HTML_TEMPLATE, width=800, height=600
        )
        self.webview_window.events.loaded += self._on_webview_html_loaded

        webview.start(gui=gui_engine, debug=False)
        self.command_queue.put(None)


def gui_process_target(command_queue):
    WindowDisplay(command_queue).run()


_gui_command_queue = multiprocessing.Queue()
_gui_process = multiprocessing.Process(
    target=gui_process_target, args=(_gui_command_queue,), daemon=True
)
_gui_started = False


def launchViewerIfNeeded():
    global _gui_started
    if not _gui_started:
        _gui_process.start()
        _gui_started = True


def sendPlotlyFigToGui(fig):
    if hasattr(fig, "to_plotly_json"):
        fig_json = fig.to_plotly_json()
        command = {"type": "PLOTLY_FIG_JSON", "payload": fig_json}
        _gui_command_queue.put(command)


# --- Simplified Demo Class ---
class Plots:

    @staticmethod
    def scatter(x, y):
        return go.Figure(go.Scatter(x=x, y=y, mode="lines+markers"))

    @classmethod
    def show_scatter(cls, x, y):
        fig = cls.scatter(x, y)
        sendPlotlyFigToGui(fig) # custom override: [UNACCEPTABLE]
        # display(fig)  # detect event and Raise
        return fig

    @classmethod
    def updateLiveScatter(cls, fig, x_new, y_new):
        if not isinstance(fig, go.Figure):
            fig = go.Figure(fig)
        xs = (
            [*fig.data[0].x, *x_new]
            if isinstance(x_new, (list, tuple))
            else [*fig.data[0].x, x_new]
        )
        ys = (
            [*fig.data[0].y, *y_new]
            if isinstance(y_new, (list, tuple))
            else [*fig.data[0].y, y_new]
        )
        fig.data[0].x = xs
        fig.data[0].y = ys
        sendPlotlyFigToGui(fig)  # custom override: [UNACCEPTABLE]
        # fig.show()  # detect event and Raise
        return fig


# --- Runtime Entry Point for Script Execution ---
if __name__ == "__main__":
    import numpy as np

    launchViewerIfNeeded()

    x_data = [1, 2, 3, 4, 5]
    y_data = [1, 2, 3, 4, 5]

    fig = Plots.show_scatter(x_data, y_data)
    for i in range(100):

        fig = Plots.updateLiveScatter(fig, i, np.sin(i / 10))
        time.sleep(0.05)

```

## 5.2 Prototype Stratergy: Environment Interface Interception - Working

```python
# Use case, the class is self aware of the context it is running in, and may locally delegate if .py,

class InsertAttribute(type):
    # Define time processing of environment
    def __new__(cls, name, bases, attrs):
        # Create the class normally
        new_class = super().__new__(cls, name, bases, attrs)

        # Set the IS_NOTEBOOK attribute based on the environment
        # Dummy overwrite of display function
        if "__file__" in globals().keys():
            new_class.IS_NOTEBOOK = False
            globals()["display"] = f  # Overwrite display to a dummy function
        else:
            new_class.IS_NOTEBOOK = True
        print(f"EnvMeta: IS_NOTEBOOK is {new_class.IS_NOTEBOOK}")
        return new_class

    # Or if you want to use __getattribute__ to dynamically set the attribute at method invocation/attribute time
    @classmethod
    def __getattribute__(cls, name):
        descr = type.__getattribute__(cls, name)
        if "__file__" in globals().keys():
            IS_NOTEBOOK = False
            # cls.IS_NOTEBOOK = False
        else:
            # cls.IS_NOTEBOOK = True
            IS_NOTEBOOK = True

        cls.IS_NOTEBOOK = IS_NOTEBOOK

        print(f"EnvMeta: IS_NOTEBOOK is {IS_NOTEBOOK}")

        return descr


def f(*args, **kwargs):
    """
    Dummy function to test the metaclass.
    """
    print("display overwrite")

```

## 5.2 Prototype Stratergy: Display Interception - Working Raise

```python

from ipykernel.kernelapp import IPKernelApp
from jupyter_client import BlockingKernelClient
from IPython.display import display
from ipykernel.connect import get_connection_file
import threading

# 1) Start an in‐process kernel
app = IPKernelApp.instance()
app.initialize(
    [
        "--IPKernelApp.no_stdout=True",
        "--IPKernelApp.no_stderr=True",
        "--IPKernelApp.log_level=ERROR",  # Or ERROR for even less
        # You might need to pass other args if your environment requires them
    ]
)  # no args: will write ~/.local/share/jupyter/runtime/kernel-<id>.json


cf = get_connection_file()
# cf = app.connection_file
client = BlockingKernelClient(connection_file=cf)
client.load_connection_file()
client.start_channels(shell=False, stdin=False)


def iopub_listener():
    while True:
        msg = client.iopub_channel.get_msg()
        if msg["msg_type"] in ("display_data", "update_display_data"):
            print("Received message:", msg)
            raise NotImplementedError(f"Dummy raise:{msg} ")
            # just to check if the listener works in the a python file since the std.out is garbage


import time

threading.Thread(target=iopub_listener, daemon=True).start()
i = 0
while i < 100:
    if i == 50:
        display("Hello from the notebook!")
    time.sleep(0.1)
    i = i + 1


```

-   **A.5. Key Test/Demo Functions for `Plots` Class (MRE based):**

```python
from IPython.display import display
import numpy as np
import plotly.graph_objects as go
import time
import ipywidgets


# --- Simplified Demo Class ---
class _demo_Plots:

    @staticmethod
    def scatter(x, y):
        return go.Figure(go.Scatter(x=x, y=y, mode="lines+markers"))

    @staticmethod
    def show_scatter(x, y):
        fig = _demo_Plots.scatter(x, y)
        # sendPlotlyFigToGui(fig)
        fig.show()
        return fig

    @staticmethod
    def updateLiveScatter(fig, x_new, y_new):
        if not isinstance(fig, go.Figure):
            fig = go.Figure(fig)
        xs = (
            [*fig.data[0].x, *x_new]
            if isinstance(x_new, (list, tuple))
            else [*fig.data[0].x, x_new]
        )
        ys = (
            [*fig.data[0].y, *y_new]
            if isinstance(y_new, (list, tuple))
            else [*fig.data[0].y, y_new]
        )
        fig.data[0].x = xs
        fig.data[0].y = ys
        # Update data on the figure
        # For FigureWidget, batch_update is better. For go.Figure, direct assignment is fine.
        if isinstance(fig, go.FigureWidget):
            with fig.batch_update():
                fig.data[0].x = xs
                fig.data[0].y = ys
        else:
            fig.data[0].x = xs
            fig.data[0].y = ys

        display(fig)  # Crucial: direct display call
        return fig

    @staticmethod
    def displayAsWidget(x_data, y_data):
        # FigureWidget is canonical for "widget" behavior in Jupyter/ipywidgets
        figure_widget = go.FigureWidget(
            data=[go.Scatter(x=x_data, y=y_data, mode="lines+markers")],
            layout=go.Layout(title="Widget Display"),  # Minimal layout
        )
        display(figure_widget)  # <<< Key: display(_widget)
        return figure_widget

    @staticmethod
    def displayInContainer(x_data, y_data):
        figure_widget = go.FigureWidget(
            data=[go.Scatter(x=x_data, y=y_data, mode="lines+markers")],
            layout=go.Layout(title="Container Display"),  # Minimal layout
        )
        # Create a minimal ipywidgets container
        simple_container = widgets.VBox([figure_widget])
        display(simple_container)  # <<< Key: display(container)
        return figure_widget, simple_container


def demo_executionCycle():
    x_data = []
    y_data = []
    fig = _demo_Plots.show_scatter(x_data, y_data)
    for i in range(100):
        fig = _demo_Plots.updateLiveScatter(fig, i, np.sin(i / 10))
        time.sleep(0.05)


def demo_executionCycle2():
    x_axis_data = []

    y_axis_data = []

    print("Live update using FigureWidget (displayAsWidget then updateLiveScatter):")
    current_figure = _demo_Plots.displayAsWidget(x_axis_data, y_axis_data)

    for i_val in range(100):
        if i_val > 0:
            pass

        current_figure = _demo_Plots.updateLiveScatter(
            current_figure, i_val, np.sin(i_val / 2.0)
        )
        time.sleep(0.1)  # Short sleep


def test_displayWidget():  # function name: camelCase
    fig_widget = _demo_Plots.displayAsWidget([10, 11, 12], [1, 2, 1])
    fig_in_container, container_widget = _demo_Plots.displayInContainer(
        [20, 21, 22], [3, 2, 3]
    )


def test_displayFig():
    fig = go.Figure(go.Scatter(x=[0], y=[0], mode="lines+markers"))
    fig = _demo_Plots.updateLiveScatter(fig, 2, 3)


def test_figShow():
    x_data = []
    y_data = []
    fig = _demo_Plots.show_scatter(x_data, y_data)


demo_executionCycle()
demo_executionCycle2()

test_displayFig()
test_figShow()
test_displayWidget()


# inline tests

x_data = []
y_data = []
fig = _demo_Plots.show_scatter(x_data, y_data)


fig = go.Figure(go.Scatter(x=[0], y=[0], mode="lines+markers"))
fig = _demo_Plots.updateLiveScatter(fig, 2, 3)


fig = go.Figure(go.Scatter(x=[0], y=[0], mode="lines+markers"))
fig = fig.show()

fig = go.Figure(go.Scatter(x=[0], y=[0], mode="lines+markers"))
fig = display(fig)
```

# Supplemental Thoughts: Alternative Approaches

While the main body of this specification details a primary set of strategies for achieving the desired dual-environment plotting behavior, several alternative or complementary approaches could be considered. These often involve different points of interception, distinct methods for controlling Plotly's output, or varied architectural setups. Each comes with its own set of advantages, disadvantages, and implications for the overall system design.

**1. Custom Plotly Renderer with Conditional Dispatch**

-   **Mechanism:** Plotly's rendering framework (`plotly.io.renderers`) allows for the definition and registration of custom renderers. A bespoke renderer could be developed specifically for the script environment. When `fig.show()` is invoked and this custom renderer is active, it would bypass standard browser output. Instead, its rendering function would serialize the figure data (e.g., to JSON or by extracting the necessary JavaScript call) and dispatch it to the `pywebview` GUI queue. The `isNotebookEnvironment()` utility would be used at application startup to conditionally set this custom renderer as the default (e.g., `plotly.io.renderers.default = 'custom_webview_renderer'`) only when executing as a script. In a notebook environment, Plotly's standard notebook renderer would remain the active default.
-   **Potential Benefits:** This approach leverages Plotly's official extension points, potentially leading to a cleaner integration for `fig.show()` calls compared to more general patching mechanisms.
-   **Considerations:** This strategy primarily addresses `fig.show()`. Calls to `IPython.display.display(fig)` might not be covered, as `IPython.display` often has its own rich display logic for Plotly figures (e.g., via `_repr_mimebundle_`) that could bypass Plotly's default renderer system. Thus, this might need to be combined with other interception methods (like IOPub or stdout monitoring) for comprehensive coverage. It also requires a working understanding of Plotly's renderer API.

**2. Conditional Monkey-Patching of Core Plotly Display Functions**

-   **Mechanism:** As an alternative to, or in conjunction with, intercepting `IPython.display.display` or `sys.stdout`, specific functions within the `plotly.io` module (such as `plotly.io.show` or lower-level functions responsible for HTML generation or browser invocation) could be directly monkey-patched. This patching would be applied conditionally at startup if `isNotebookEnvironment()` returns false. The patched function would then reroute the figure data to the `pywebview` GUI queue instead of performing its default action.
-   **Potential Benefits:** This method can be highly targeted for controlling the behavior of `fig.show()` calls.
-   **Considerations:** Direct monkey-patching of library internals is generally considered more brittle than using official APIs. Such patches are vulnerable to breaking if Plotly library internals change with updates. Similar to custom renderers, this might not comprehensively cover `IPython.display.display(fig)` calls. The current specification favors less invasive interception where possible, though it does allow for controlled patching of `DisplayPublisher`.

**3. Wrapper/Proxy Objects for Plotly Figures**

-   **Mechanism:** This approach would involve a more significant conceptual shift. When methods within the `Plots` class (like `createGraph`) generate a Plotly figure object (`go.Figure` or `go.FigureWidget`), they could return a custom wrapper or proxy object instead of the raw Plotly object. This wrapper would encapsulate the actual Plotly figure. The wrapper object would be designed to:
    -   Implement `_repr_mimebundle_` (or `_repr_html_`) to ensure correct rendering in Jupyter notebooks by delegating to the wrapped figure's rich representation methods.
    -   Provide a custom `show()` method that, when executed in a script environment, sends the figure data to the `pywebview` GUI queue. In a notebook environment, this custom `show()` would simply call the wrapped figure's original `show()` method.
    -   Delegate all other attribute and method accesses to the underlying Plotly figure to maintain compatibility as much as possible.
-   **Potential Benefits:** This could encapsulate the dual-display logic more directly within the figure-like object itself.
-   **Considerations:** This would necessitate modifications to the `Plots` class's internal logic to return these wrapped objects. While public method signatures might remain the same, the _type_ of the returned object would change, potentially breaking user code that performs strict type checking or relies on specific Plotly object methods that are not perfectly proxied. Handling `IPython.display.display(wrapped_fig)` in scripts would also need careful design. This represents a notable deviation from the current specification's preference for external interception.

**4. Local Web Server with `pywebview` Pointing to `localhost`**

-   **Mechanism:** Instead of directly injecting JavaScript into the `pywebview` instance or sending full figure JSON for `Plotly.react`, the main Python script (when in script mode) could initiate and manage a very lightweight, local HTTP server (e.g., using Python's `http.server` module or a minimal Flask/FastAPI application) running in a separate thread. When a plot needs to be displayed or updated, the main script would generate the full HTML page for the Plotly figure (or update a static file served by this local server). The `pywebview` window would then be configured to simply load a URL from this local server (e.g., `http://localhost:PORT/plot.html`). Updates to the plot would involve the main script updating the HTML/data on its local server and then signaling `pywebview` to reload its current page, or potentially using JavaScript within the `webview` to fetch new data from a local API endpoint provided by the embedded server.
-   **Potential Benefits:** This approach significantly decouples `pywebview` from the plotting logic; `pywebview` essentially becomes a simple "browser" view for locally served web content. It could simplify the JavaScript injection aspect if `pywebview` primarily handles page reloads. Debugging the generated HTML/JS might also be easier, as it could be opened and inspected in a standard web browser.
-   **Considerations:** This introduces an additional component (the local HTTP server) that requires management (port selection, thread safety, lifecycle). Communication for plot updates might become more indirect. Rapid updates (e.g., from interactive sliders) could feel less "live" if they necessitate full page reloads, unless more sophisticated techniques like WebSockets or JavaScript fetching from local API endpoints are implemented, which would add back complexity.

**5. Asynchronous `pywebview` Integration in the Main Process (Thread-Based)**

-   **Mechanism:** The current specification generally implies that `pywebview` runs in a separate `multiprocessing.Process` to ensure GUI responsiveness and avoid blocking the main script. An alternative architecture could involve running `pywebview` in a separate _thread_ within the main Python process. Communication between the main application logic and the GUI thread would then use thread-safe queues (e.g., Python's standard `queue.Queue`) instead of `multiprocessing.Queue`.
-   **Potential Benefits:** This could avoid the overhead and some complexities of inter-process communication (e.g., data serialization can be simpler as objects do not need to be pickled for transfer between processes). Communication between the main logic and the GUI thread might potentially be faster.
-   **Considerations:** Due to Python's Global Interpreter Lock (GIL), true parallelism is not achieved for CPU-bound tasks, although GUI event loops are often I/O bound and can function effectively in threads. However, integrating GUI event loops correctly within threads in a potentially blocking main application can be challenging, and behavior can vary across different platforms and GUI backends used by `pywebview`. The thread safety of `pywebview` itself and its event loop integration would need careful validation to prevent issues like a non-responsive main application or deadlocks.

**6. Dedicated "Display Server" Process with a Richer API**

-   **Mechanism:** Rather than relying on a simple queue for JavaScript strings or JSON payloads, the GUI process could expose a more structured Application Programming Interface (API). This could be achieved using mechanisms like `multiprocessing.managers.BaseManager` to create shared objects or remote procedure calls (RPC), or by employing libraries such as ZeroMQ. The main script would then interact with this API through calls like `display_server.new_plot(figure_json_data)` or `display_server.update_plot_data(target_plot_id, new_data_payload)`.
-   **Potential Benefits:** This could provide a cleaner and more extensible API for interaction with the GUI window, especially if more complex interactions are envisaged for the future (e.g., managing multiple distinct plot views within the same window, or retrieving data or events back from the GUI to the main script).
-   **Considerations:** This approach would add significant complexity to the inter-process communication (IPC) mechanism compared to a simple queue. It is likely an over-engineering for the currently defined requirements but could be a future evolution if the system's capabilities need to expand substantially.
