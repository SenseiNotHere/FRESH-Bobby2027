# Bobby 2027 - Offseason Rebuild

FRC Team 1811’s offseason development codebase.

Also known as Bobby the Box.
For close friends, just Bobby.
Pronouns: She/Her.

Fully state-driven.  
Fully superstructured.  
Fully rebuilt for experimentation.

This is the offseason iteration. Testing new control patterns, command structures, and autonomous workflows without match pressure.

---

# 🧠 Architecture Philosophy

We don’t bind buttons straight to motors anymore.

We define intent.

States like `PREP_SHOT`, `INTAKING`, `APPROACHING_TOWER` describe what the robot is trying to accomplish. The superstructure then coordinates drivetrain, shooter, intake, and everything else accordingly.

Clean. Predictable. Scalable.

Teleop and auto share logic.  
Subsystems don’t fight each other.  
And we’re not duct-taping commands together mid-event anymore.

We’re building like we plan to keep winning with it.

---

# ➕ Adding a New State

States are the brain of this robot.

Adding a new state is easy-peasy, but requires a little bit of thinking.

Here’s the process.

------------------------------------------------------------------------

## 1️⃣ Define the State

Go to:

    superstructure/robot_state.py

Add your new enum value inside `RobotState`.

Example:

``` python
class RobotState(Enum):
    ...
    ALIGNING_TO_TARGET = 99
```

Keep it descriptive.  
Make it very specific.

Bad:

``` python
RUN_SHOOTER_FAST
```

Good:

``` python
PREP_SHOT
ALIGNING_TO_TARGET
APPROACHING_TOWER
```

------------------------------------------------------------------------

## 2️⃣ Route It in `__init__()`

Open:

    superstructure/superstructure.py

Inside the `__init__()` method, add your state to the `_state_handlers` dictionary:

``` python
RobotState.ALIGNING_TO_TARGET: self._handle_aligning_to_target,
```

Note: The handler itself will be defined in a separate file (see step 3).

------------------------------------------------------------------------

## 3️⃣ Create the Handler

Open:

    superstructure/superstructure_states.py

Define the handler method inside the `SuperstructureStates` class:

``` python
def _handle_aligning_to_target(self: "Superstructure"):
    if not self.hasVision or not self.drivetrain:
        return

    self.drivetrain.alignToTarget(self.vision)
```

**Important:** Always include the type hint `self: "Superstructure"` to ensure the IDE can resolve references to other subsystems and states.

Handlers should:

-   Coordinate subsystems  
-   Not contain low-level hardware code  
-   Not bypass subsystem safety checks

Subsystems execute.  
Superstructure decides.

------------------------------------------------------------------------

## 4️⃣ Special Helpers

If your new state requires utility functions, they belong in:

- `superstructure/superstructure_helpers.py`: For utility methods (e.g., stopping multiple subsystems).

------------------------------------------------------------------------

## 5️⃣ (Optional) Add Readiness Logic

If your new state affects robot readiness (for example, shooter ready, intake deployed, etc.), update `_update_readiness()` accordingly.
This is the correct place to add safety checks, gating logic, or state-based conditions.
If you introduce a new readiness flag, make sure to also add it to the `RobotReadiness` data class located in:
    superstructure/robot_state.py
All readiness values should live inside `RobotReadiness`. Please don't scatter them all over the codebase.

Keep readiness centralized.

This keeps rumble logic, feed gating, and state transitions consistent.

Optional: But you may want to add your readiness flag to the `ReadinessList` enum. 100% optional.
It'll allow you to use `setRobotReadiness()` and `getRobotReadiness()` methods with those flags.

------------------------------------------------------------------------

## 6️⃣ Transition Properly

To enter your new state:

``` python
self.superstructure.setState(RobotState.ALIGNING_TO_TARGET)
```

Or create a reusable command:

``` python
self.superstructure.createStateCommand(RobotState.ALIGNING_TO_TARGET)
```

Do NOT:

-   Call subsystem motors directly from button bindings  
-   Mix superstructure logic inside commands

Intent flows through state.

------------------------------------------------------------------------

## 🧠 Design Guidelines

When adding a state, ask:

-   Is this a robot intention?  
-   Can teleop and auto reuse it?

If yes -> it belongs as a state.

---

Architecture first.  
Results follow.


# ⚙ Subsystem Overview

## 🔄 Drivetrain - Kraken Swerve

Located in `subsystems/drive/`

- Drive Motors: Kraken X60
- Steer Motors: Kraken X44
- Holonomic swerve drive
- Field-relative control
- Pose / odometry support
- Vision-assisted alignment

Yes, it's fast.
Yes, it tracks.
Yes, it behaves.

---

## 🎯 Shooter System

Located in `subsystems/shooter/`

- Shooter Motors: Kraken X60
- Closed-loop velocity control
- Superstructure-coordinated spin-up
- Readiness-based firing logic

We don't just press shoot and pray.
The robot confirms it's ready.

---

## 📦 Indexer

Located in `subsystems/shooter/`

- Motor: Brushless motor via Spark MAX
- Velocity-controlled feed/reverse behavior
- Controlled by superstructure
- Only feeds when shooter conditions are met

No panic feeding. No chaos cycling.

---

## 😵‍💫 Agitator

Located in `subsystems/shooter/`

- Motor: NEO Brushless motor via Spark MAX
- Supports feed, reverse, and oscillation behavior
- Used to keep game pieces moving cleanly through the system

It shakey-shakey, we like it when it shakey-shakey.

---

## 🟢 Intake

Located in `subsystems/intake/`

- Deploy motor: NEO Brushless motor via Spark MAX
- Roller motor: Kraken X60
- Homing with limit switches
- Deploy / stow control
- Pulse behaviors for intake and position

It deploys when it should.
It retracts when it should.
Ground intake energy handled.

---

## 👁 Vision System

Located in `subsystems/vision/`

- Limelight-based targeting
- AprilTag localization support
- Pipeline switching
- Camera heartbeat / detection monitoring
- Target-aware scoring support

Vision is baked into decision-making.
It is NOT a side feature.

---

## 🎵 Orchestra

Located in `subsystems/orchestra/`

- Phoenix 6 Orchestra integration
- Uses registered Kraken motors as instruments
- Dashboard song selection
- CHRP playback support

Yes, the robot can sing.
Yes, that is a feature.
No, we will not apologize.

---

# 🤖 Autonomous

- PathPlanner integration (`deploy/pathplanner/`)
- Auto-discovery of routines from deploy folder
- Shared superstructure logic with teleop
- Vision-assisted pathfinding
- Driver-controlled path selection

Auto runs on the same brain as teleop.

Consistency >>> copy-paste command stacks.

---

# 🛠 Tech Stack

- Python 3.14+
- RobotPy + WPILib
- Commands v2
- Phoenix 6
- REV
- PathPlanner
- Limelight
- PyKit (logging & replay)

Yes, we use logging to debug. Yes, offseason means we experiment.

---

# ⚠ IMPORTANT WARNINGS (PLEASE READ BEFORE YOU FAFO)

## 🔧 Robot-Specific Constants

**ALL CONSTANTS IN THIS REPOSITORY ARE ROBOT-SPECIFIC.**

Every value in `constants/` is tuned for:

- Our gear ratios  
- Our inversions  
- Our encoder offsets  
- Our CAN IDs  
- Our robot dimensions  
- Our pneumatics  

If you copy this without changing constants… respectfully… that’s wild.

You MUST:

- Verify CAN IDs  
- Verify inversions  
- Verify encoder offsets  
- Retune all PID values  
- Confirm dimensions  

Failure to update constants may result in:

- Mechanism damage  
- Uncontrolled motion  
- Incorrect field positioning  
- Serious injury  

Yes. Injury.

Misconfigured control loops can cause sudden, high-speed robot movement.

By using this repository, you accept full responsibility for safe implementation.  
FRC Team 1811 is not liable for damage, injury, or misuse.

This is not a plug-and-play template.  
This is architecture.

---

## 🔐 Phoenix 6 Pro Requirement

This robot uses CTRE Phoenix 6 Pro features.

Without:

- A valid Phoenix Pro license  
- Correct Phoenix installation  
- Matching firmware  

Some motors and advanced control modes will not behave properly.

Set up your CTRE stack correctly before deploying.

We are not debugging your licensing.

---

# 🧪 Development Setup

## 1. Create a virtual environment

    python -m venv .venv

Then activate it:

**Windows (PowerShell):**

    .\.venv\Scripts\Activate.ps1

**Windows (Command Prompt):**

    .\.venv\Scripts\activate.bat

**macOS/Linux:**

    source .venv/bin/activate

## 2. Install dependencies

    pip install -r requirements.txt

## 3. Sync RobotPy dependencies

    robotpy sync

## 4. Run in simulator

    robotpy sim

## 5. DEPLOY AND ENJOY!!

    robotpy deploy --skip-tests

---

# 🎮 Button Bindings

Located in `button_bindings.py`

Driver and operator bindings are centralized here. Bindings route to state commands via the superstructure, not directly to motors.

**Driver Controls:**
- POV (D-Pad): Odometry reset and heading reset
- Bumpers & Triggers: Aiming, intake, shooting
- Face Buttons: Special behaviors (agitator, music)

**Operator Controls:**
- Triggers: Intake control (fwd/reverse)
- Bumpers: Deploy/stow intake
- Buttons: Manual pivot control

All bindings go through `RobotState` transitions. No motor calls in button handlers.

---

- Use RobotPy simulation tools  
- Or deploy to a roboRIO  

Follow RobotPy + WPILib documentation for deployment instructions.

---

# 📁 Project Structure

    .gitignore
    pyproject.toml
    requirements.txt
    robot.py
    robot_container.py
    button_bindings.py
    commands/
    constants/
    deploy/
    subsystems/
    superstructure/
    utils/

---

# 🎵 Music / CHRPs

CHRPs are in:

    deploy/files

Yes, the robot can sing.
Yes, it likely will be Ariana Grande.
Yes, that's intentional.

---

# 🤝 How to Contribute

Welcome.

If you're contributing, that means you care about building something clean. We appreciate that.

This robot runs on a state-driven architecture. Respect the structure.

## 🧠 Before You Add Code

- Do not bypass the superstructure.
- Do not bind buttons directly to motor outputs.
- Do not hardcode constants outside `constants/`.
- If you’re unsure where something belongs: ask.

We build systems here. Not shortcuts.

---

## 🗂 Organization Rules

- `subsystems/` -> Hardware logic (organized into: driving, intake, shooting, vision, orchestra)
- `commands/` -> Behaviors and command flows
    - `driving/`: Drivetrain behaviors (arcade drive, swerve movement, aiming, pathfinding)
    - `intake/`: Intake deployment and roller control
    - `shooting/`: Shooter spin-up and feed logic
    - `auto/`: Autonomous routines (approach, trajectory following, vision-based movements)
    - `orchestra/`: Music playback commands
- `superstructure/` -> Robot intent coordination (divided into:)
    - `superstructure.py`: Main state machine & API
    - `superstructure_states.py`: Robot behavior state handlers
    - `superstructure_helpers.py`: Utility & helper functions
    - `robot_state.py`: State definitions and readiness data
    - `auxiliary_actions.py`: Supporting actions
- `constants/` -> Tunable values (constants.py, field_constants.py)
- `deploy/` -> PathPlanner assets and CHRP files
- `utils/` -> Helper tools

If it feels like a hack, it probably is.

---

## 🧪 Test First

- Run simulation before deploying.
- Verify motor directions after mechanical changes.

The robot moves fast.  
Mistakes move faster.

---

Keep it readable.  
Keep it intentional.  
Keep it experimental; this is offseason.

We're testing patterns, trying new command structures, and building the foundation for next season without match pressure.

---

Architecture first.  
Learning follows.

Built with love by FRC Team 1811 - FRESH.  
Offseason 2027.
