# LaTeX Formula Writing Guide for Research Papers

## Common LaTeX Syntax Errors and Corrections

### 1. Dot Notation Errors
- ❌ **Wrong**: `\c\dot r` 
- ✅ **Correct**: `\dot{r}` (for time derivative)
- ✅ **Correct**: `q \cdot x` (for dot product)

### 2. Matrix Environment Misuse
- ❌ **Wrong**: Using `\begin{bmatrix}...\end{bmatrix}` for grouping terms
- ✅ **Correct**: Use parentheses `()` or brackets `[]` for grouping
- ✅ **Correct**: Only use matrix environments for actual matrices

### 3. Mixed Syntax Errors
- ❌ **Wrong**: Mixing `$$` with code blocks
- ❌ **Wrong**: `\left$ ... \right \\`
- ✅ **Correct**: Use consistent delimiters

### 4. Operator Formatting
- ❌ **Wrong**: `tr` or `Im` (italicized like variables)
- ✅ **Correct**: `\operatorname{tr}` or `\operatorname{Im}`

## Correctly Formatted Physics Formulas

### Hamiltonian and Related Definitions

**Equation (1) - Total Hamiltonian:**
```latex
H(t) = H_{0} + H_{ex}(t)
```

where
```latex
H_{0} = \sum_{k} \varepsilon_{k} c^\dagger_{k} c_{k} + u_{i} V \sum_{n} \sum_{k,p} e^{ip \cdot \dot{r}_{n}} c^\dagger_{k-p} c_{k}
```

and
```latex
H_{ex}(t) = -J \sum_{k,q} (c^\dagger_{k-q} \hat{\sigma} c_{k}) \cdot \dot{S}_{q}(t)
```

**Electron-Spin Density:**
```latex
\rho_{s}^\alpha(x,t) \equiv \frac{\hbar}{2} \operatorname{tr} \langle \psi^\dagger(x,t) \hat{\sigma}^\alpha \psi(x,t) \rangle_{H}
```

**Equation (2) - Spin Current Density:**
```latex
j_{s}^\alpha(x,t) = -i \frac{\hbar^{2}}{2m} \frac{1}{V} \sum_{k,q} e^{-iq \cdot x} k \operatorname{tr} \left[ \hat{\sigma}^\alpha \hat{G}^<_{k-\frac{q}{2}, k+\frac{q}{2}}(t,t) \right]
```

### Pumped Spin Current Calculations

**Equation (3) - First-order contribution to spin current:**
```latex
j_{s}^{\alpha(1)}(x,t) = -2 \frac{\hbar^{3} J}{m V} \sum_{k,k',q} \sum_{\omega, \Omega} e^{-iq \cdot x + i\Omega t} S_{q}^\alpha(\Omega) q \Omega f'(\omega) \operatorname{Im}[\varepsilon_{k} g^{r}_{k,\omega} (g^{a}_{k,\omega})^{2}] \left( 1 + n_{i} u_{i}^{2} V \Pi^{ra}(q; \omega, \Omega) g^{r}_{k',\omega} g^{a}_{k',\omega} \right)
```

**Equation (4) - Diffusion Ladder (Vertex Correction):**
```latex
\Pi^{ra}(q; \omega, \Omega) \equiv \sum_{n=0}^\infty \left( \sum_{k} n_{i} u_{i}^{2} V g^{r}_{k-\frac{q}{2}, \omega - \frac{\Omega}{2}} g^{a}_{k+\frac{q}{2}, \omega + \frac{\Omega}{2}} \right)^{n}
```

**Equation (5) - Dominant first-order contribution to the spin current:**
```latex
j_{s}^{\alpha(1)}(x,t) = \hbar \nu J \tau D \nabla \langle \dot{S}^\alpha(x,t) \rangle_{V}
```

**Equation (6) - Long-range diffusion due to random impurity scattering:**
```latex
\langle A(x,t) \rangle_{V} \equiv \frac{1}{V} \int d^{3}x' \int dt' \sum_{q} \sum_\Omega e^{-iq \cdot (x-x') + i\Omega(t-t')} \frac{A(x', t')}{Dq^{2} \tau + i\Omega \tau}
```

**Equation (7) - Dynamic component of the second-order contribution:**
```latex
j_{s}^{\alpha(2)}(x,t) = -4 \frac{\hbar^{2} J^{2} \tau^{3}}{m V} \sum_{k,k',q,q'} \sum_{\omega, \Omega, \Omega'} e^{-iq \cdot x + i\Omega t} (S_{q',\Omega'} \times S_{q-q', \Omega - \Omega'})^\alpha \Omega' f'(\omega) \operatorname{Im}[\varepsilon_{k} g^{r}_{k,\omega} (g^{a}_{k,\omega})^{2}] \left( (q+q') + n_{i} u_{i}^{2} \frac{i q}{V} \Pi^{ra}(q; \omega, \Omega) g^{r}_{k',\omega} g^{a}_{k',\omega} \right)
```

which simplifies to:
```latex
j_{s}^{\alpha(2)}(x,t) \simeq -2 \nu J^{2} \tau^{2} D \nabla \langle [S(x,t) \times \dot{S}(x,t)]^\alpha \rangle_{V}
```

**Equation (8) - Equilibrium component (spin super-current):**
```latex
j_{sc}^{\alpha(2)}(x,t) = i \frac{\hbar^{2} J^{2}}{m V} \sum_{k,q,q'} \sum_{\omega, \Omega, \Omega'} e^{-iq \cdot x + i\Omega t} (S_{q',\Omega'} \times S_{q-q', \Omega - \Omega'})^\alpha q' f'(\omega) \operatorname{Im}[(g^{a}_{k,\omega})^{2}]
```

which simplifies to:
```latex
j_{sc}^{\alpha(2)}(x,t) \simeq - \frac{\hbar^{2}}{2} \nu J^{2} \frac{1}{2m \varepsilon_{F} V} [S(x,t) \times \nabla S(x,t)]^\alpha
```

### Effective Potentials and Currents

**Equation (9) - Pumped spin current as gradient:**
```latex
j_{s}^{(p)\alpha}(x,t) = - \nabla \mu_{s}^\alpha(x,t)
```

**Equation (10) - Effective spin potential:**
```latex
\mu_{s}^\alpha(x,t) = - \hbar \nu J \tau D \langle \dot{S}^\alpha(x,t) \rangle_{V} + 2 \nu J^{2} \tau^{2} D \langle [S(x,t) \times \dot{S}(x,t)]^\alpha \rangle_{V}
```

**Equation (11) - Spin Density:**
```latex
\rho_{s}^\alpha(x,t) = - \hbar \nu J \tau D \nabla^{2} \langle S^\alpha(x,t) \rangle_{V} + 2 \nu J^{2} \tau^{2} \langle [S(x,t) \times \dot{S}(x,t)]^\alpha \rangle_{V}
```

**Equation (12) - Spin Diffusion Equation:**
```latex
\dot{\rho}_{s}^\alpha(x,t) - D \nabla^{2} \rho_{s}^\alpha(x,t) = \tau_\rho^\alpha(x,t)
```

**Equation (13) - Spin Relaxation:**
```latex
\tau_\rho^\alpha(x,t) = - \hbar \nu J D \nabla^{2} S^\alpha(x,t) + 2 \nu J^{2} \tau [S(x,t) \times \dot{S}(x,t)]^\alpha
```

**Equation (14) - Effective Spin Potential (rewritten):**
```latex
\mu_{s}^\alpha(x,t) = D \rho_{s}^\alpha(x,t) - \hbar \nu J D \frac{1}{V} S^\alpha(x,t)
```

**Equation (15) - Total Spin Current:**
```latex
j_{s}^\alpha(x,t) = j_{sc}^{\alpha(2)}(x,t) + j_{s}^{(p)\alpha}(x,t) = - \frac{\hbar^{2}}{2} \nu J^{2} \frac{1}{2m \varepsilon_{F} V} [S(x,t) \times \nabla S(x,t)]^\alpha - \nabla \mu_{s}^\alpha(x,t)
```

**Equation (16) - Total Spin Current (with spin density):**
```latex
j_{s}^\alpha(x,t) = j_{sc}^\alpha(x,t) - D \nabla \rho_{s}^\alpha(x,t)
```

**Equation (17) - Total Equilibrium Spin Current:**
```latex
j_{sc}^\alpha(x,t) = \hbar \nu J D \frac{1}{V} \nabla S^\alpha(x,t) - \frac{\hbar^{2}}{2} \nu J^{2} \frac{1}{2m \varepsilon_{F} V} [S(x,t) \times \nabla S(x,t)]^\alpha
```

**Equation (18) - Charge Current:**
```latex
j_{c}(x,t) = \sigma_{c} E(x,t) + j_{sc}(x,t) - D \nabla \rho_{c}(x,t)
```

**Equation (19) - Generalized Spin Current with Spin-Orbit Interactions:**
```latex
j_{si}^\alpha(x,t) = \sigma_{SH} \epsilon_{ij\alpha} E_{j}(x,t) + j_{si}^{(sc)\alpha}(x,t)
```

## LaTeX Best Practices for Physics

1. **Use proper operators**: `\operatorname{tr}`, `\operatorname{Im}`, `\operatorname{Re}`
2. **Correct derivatives**: `\dot{S}` for time derivatives, `\nabla` for spatial derivatives
3. **Proper spacing**: Use `\,` for thin space, `\quad` for medium space
4. **Vector notation**: Use `\vec{v}` or just bold letters
5. **Matrix environments**: Only use for actual matrices/arrays
6. **Delimiters**: Use `\left(` and `\right)` for auto-sizing parentheses
7. **Subscripts/Superscripts**: Always use braces for multi-character: `_{abc}` not `_abc`

## Testing Your LaTeX

Before using formulas in your application, test them in:
- Online LaTeX editors (Overleaf, LaTeX Live)
- MathJax demo pages
- KaTeX demo pages

This ensures proper rendering before integration into your research interface.
