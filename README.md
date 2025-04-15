\documentclass[a4paper,12pt]{article}
\usepackage{amsmath}
\usepackage{amssymb}
\usepackage{geometry}
\geometry{left=2cm,right=2cm,top=2cm,bottom=2cm}

\title{Lyapunov Control of Predator-Prey-Food Ecosystem}
\author{}
\date{}

\begin{document}

\maketitle

\section*{Problem Description}

We simulate and control a simplified ecosystem using a dynamical systems framework. 
The ecosystem consists of three interacting populations:

\begin{itemize}
    \item \textbf{Food (F)}: A renewable resource.
    \item \textbf{Prey (P)}: Herbivores that consume food.
    \item \textbf{Predators (R)}: Carnivores that consume prey.
\end{itemize}

Our objective is to control this system using feedback such that the state $(F, P, R)$ converges to a desired target equilibrium.

\section*{State Space Description}

The system's state is described by the vector:
\[
x = \begin{bmatrix} f \\ p \\ r \end{bmatrix},
\]
where
\begin{itemize}
    \item $f$: amount of food,
    \item $p$: number of prey,
    \item $r$: number of predators.
\end{itemize}

\section*{Action Space Description}

The control action vector \( u \in \mathbb{R}^3 \) is defined as
\[
u = \begin{bmatrix} a_1 \\ a_2 \\ a_3 \end{bmatrix},
\]
where
\begin{itemize}
    \item $a_1$: control input influencing food supply,
    \item $a_2$: control input influencing prey population,
    \item $a_3$: control input influencing predator population.
\end{itemize}

\section*{System Dynamics}

The dynamics are modeled as a set of nonlinear differential equations:
\[
\begin{cases}
\dot{f} = k f - \alpha p + a_1, \\
\dot{p} = \beta f p - \gamma r + a_2, \\
\dot{r} = \delta p r - \mu r + a_3,
\end{cases}
\]
where
\begin{itemize}
    \item $k$: food influx rate,
    \item $\alpha$: rate of food consumption by prey,
    \item $\beta$: prey growth efficiency due to food,
    \item $\gamma$: predation rate,
    \item $\delta$: predator growth efficiency due to prey,
    \item $\mu$: predator death rate.
\end{itemize}

\section*{Lyapunov-Based Control}

To stabilize the system to a desired target state
\[
x^* = \begin{bmatrix} f^* \\ p^* \\ r^* \end{bmatrix},
\]
we employ Lyapunov-based feedback control. The Lyapunov function is chosen as a quadratic energy function:
\[
V(x) = (x - x^*)^\top Q (x - x^*).
\]

In our implementation, the matrix \( Q \) is chosen as the identity matrix \( I \), which simplifies the Lyapunov function to:
\[
V(x) = (f - f^*)^2 + (p - p^*)^2 + (r - r^*)^2.
\]

\subsection*{Properties of the Lyapunov Function}

\begin{enumerate}
    \item \textbf{Positive Semi-Definite}:
    \[
    V(x) \geq 0, \quad \forall x,
    \]
    with equality if and only if \( x = x^* \).

    \item \textbf{Time Derivative of the Lyapunov Function}:

    Let the error vector be \( e = x - x^* \). Then, the time derivative of \( V \) is
    \[
    \dot{V}(x) = 2 (f - f^*) \dot{f} + 2 (p - p^*) \dot{p} + 2 (r - r^*) \dot{r}.
    \]

    The controller is designed such that \( \dot{V}(x) \leq 0 \), ensuring stability and convergence to the equilibrium point.
\end{enumerate}

\section*{Controller and Class Structure}

The system is implemented using a modular, class-based structure with clear responsibilities:
\begin{itemize}
    \item \textbf{Plant (Ecosystem) Class}: Implements the system dynamics and state evolution.
    \item \textbf{Controller Class}: Implements the Lyapunov-based feedback controller to compute control actions based on the current state.
    \item \textbf{Simulation Class}: Runs the simulation loop, applying control actions and updating the system state.
    \item \textbf{Animator Class}: Visualizes the evolution of the system state over time.
\end{itemize}

\end{document}
