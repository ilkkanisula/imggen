# Prompting Guide: Using Reference Images

## Overview

Reference images guide the model to maintain certain visual characteristics while applying transformations. Success depends on clear prompting that tells the model what to preserve and what to change.

## When to Use Reference Images

**Pose Control**: Change pose or position while maintaining identity
```
Use case: "I want the same person in a different pose"
Models excel at: Subtle pose adjustments with identity preservation (OpenAI high fidelity)
```

**Style Transfer**: Apply artistic styles or aesthetic changes from reference
```
Use case: "I want this scene in a different visual style"
Models excel at: Color palette, lighting, composition transfers
```

**Multi-Person Compositions**: Build scenes with multiple people
```
Use case: "I want these people together in a specific arrangement"
Models excel at: Google with explicit role assignment (up to 5 people)
```

**Product Variations**: Generate variations on an existing item or scene
```
Use case: "Show this product in different colors/settings"
Models excel at: Clothing colors, background variations, similar scenes
```

## OpenAI Prompting Patterns

### Single Reference with input_fidelity

The `input_fidelity` parameter controls how strictly the model preserves facial features.

**Pattern for high fidelity (identity preservation):**
```
imggen -p "change background to beach, preserve face and pose" portrait.jpg --input-fidelity high
```

Structure:
1. Reference declaration (implicit - reference is provided)
2. Identity constraint: "preserve face and pose" / "keep facial features"
3. Change description: "change background to beach"
4. Invariant reminder: specific details to maintain

**Pattern for low fidelity (style reinterpretation):**
```
imggen -p "reimagine in oil painting style, artistic interpretation" portrait.jpg --input-fidelity low
```

Use low fidelity when you want the model to be creative with facial interpretation while keeping composition.

### Detailed Example: Pose Control

**Goal**: Change pose while preserving identity

```bash
# With high fidelity for maximum identity preservation
imggen -p "Change pose to sitting. Subject sitting in wooden chair. Preserve facial features and body posture identity. Same clothing. Indoor studio background." person.jpg --input-fidelity high
```

**Why this works:**
- Explicit "preserve facial features" tells model to maintain identity
- Clear pose change instruction: "sitting in wooden chair"
- Specifies what stays same: "clothing", "body posture identity"
- Provides context: "studio background"

**If identity isn't preserved well**, you can:
1. Try more explicit identity constraints: "maintain exact facial features and expression"
2. Use simpler pose changes (less dramatic movement)
3. Provide more context in prompt about clothing and body characteristics

### Multiple References

OpenAI supports multiple reference images to blend styles, compose multiple elements, or combine references into one coherent image.

**Pattern:**
```bash
imggen -p "Blend references: combine pose from ref1, style from ref2, background from ref3" ref1.jpg ref2.jpg ref3.jpg --input-fidelity high
```

**Use cases:**
- Style blending: One image for pose, another for artistic style
- Multi-element composition: Combine person, clothing style, and scene references
- Creative fusion: Merge elements from multiple visual references into one

When using multiple references, mention them explicitly in the prompt to guide the model:
```bash
imggen -p "Using first image as subject and pose, second image for style: render subject in style of ref2, in environment of ref3" subj.jpg style.jpg bg.jpg --input-fidelity high
```

## Google Prompting Patterns

### Single Reference

```bash
imggen -p "subject sitting in cafe, warm lighting" person.jpg --model gemini-3-pro-image-preview
```

Google works well with simple reference usage, though multiple references unlock more capability.

### Multiple References with Explicit Indexing

**Pattern:**
```bash
imggen -p "Person 1 (first image): [position/action]. Person 2 (second image): [position/action]. Scene context: [environment]." person1.jpg person2.jpg --model gemini-3-pro-image-preview
```

**Structure:**
1. Index reference: "Person 1 (first image):" / "Person 2 (second image):"
2. Position/action: Explicitly describe what you want from this reference
3. Scene context: Overall environment and lighting
4. Interaction (if relevant): How figures relate to each other

### Detailed Example: Fashion Editorial Scene

**Goal**: Two models in coordinated styling for a magazine shoot

```bash
imggen -p "
Person 1 (first image): Standing on left, wearing red structured jacket, looking towards camera.
Person 2 (second image): Standing on right, wearing navy minimalist dress, looking at Person 1.
Scene: Minimalist white studio with subtle gradient background, professional fashion photography lighting, both models with confident poses, editorial quality." model1.jpg model2.jpg --model gemini-3-pro-image-preview
```

**Why this works:**
- Clear reference indexing: "Person 1 (first image)" matches first image
- Specific clothing descriptions guide model
- Position relationships described: "Standing on left" / "looking at Person 1"
- Professional context: "editorial quality", "fashion photography lighting"
- Spatial composition: "left" and "right" positioning

### Detailed Example: Product Display with Context

**Goal**: Show product with multiple styling references

```bash
imggen -p "
Product (first image): Beautiful ceramic vase, positioned center-front.
Context 1 (second image): Styling inspiration - warm earthy color palette.
Context 2 (third image): Styling inspiration - natural botanical setting.
Scene: High-end home decor photography, warm natural lighting, wooden surfaces, fresh flowers scattered around, luxury magazine aesthetic, shallow depth of field, product is featured and in focus." vase.jpg earthy_palette.jpg botanical.jpg --model gemini-3-pro-image-preview
```

This uses multiple references to guide both the product appearance and the styling context.

### Guidelines for Multiple References

1. **Always use indexing**: "First image:", "Second image:", etc.
2. **Be specific about roles**: "Person 1", "Product", "Background reference", etc.
3. **Describe positioning**: "left side", "center", "background" creates spatial understanding
4. **Include interaction**: How multiple elements relate to each other
5. **Limit to necessary references**: 2-3 references often work best; more references require more detailed prompting

## Common Use Cases with Examples

### Pose Control (OpenAI recommended)

**Scenario**: You have a portrait and want the person in a different pose

```bash
# Sitting pose change
imggen -p "Subject sitting cross-legged on modern sofa. Preserve facial features and expression. Same clothing as reference. Warm indoor lighting." portrait.jpg --input-fidelity high

# Standing with arm position change
imggen -p "Standing with arms crossed. Preserve facial identity and body proportions. Same outfit. Professional headshot lighting." headshot.jpg --input-fidelity high
```

### Style Transfer

**Scenario**: Apply artistic style from reference to a scene

```bash
# Painting style transfer
imggen -p "Reimagine in impressionist oil painting style. Maintain composition and scene elements. Soft brushstrokes, muted color palette inspired by reference." landscape.jpg --input-fidelity low

# Photography style transfer
imggen -p "Apply vintage film photography aesthetic. Warm color grading, film grain, soft focus. Keep scene composition from reference." photo.jpg --input-fidelity low
```

### Multi-Person Scene (Google recommended)

**Scenario**: Create a group scene with multiple people

```bash
imggen -p "
Person 1 (first image): Seated on left side of couch, relaxed posture.
Person 2 (second image): Standing behind couch, smiling, hand on couch back.
Scene: Modern living room, evening lighting, large windows with city skyline, warm lamps, comfortable contemporary furniture, candid lifestyle photography, warm color temperature." person1.jpg person2.jpg --model gemini-3-pro-image-preview
```

### Product Variation

**Scenario**: Generate clothing item in different colors or styles

```bash
# Single reference with color variation
imggen -p "Same dress design as reference. Color variation: deep emerald green. Same model pose and proportions. Professional fashion photography, white background, studio lighting." dress_navy.jpg --input-fidelity high

# Multiple references: design + color style
imggen -p "Design from first image, color inspiration from second image. Render dress in the palette of reference 2, keeping silhouette from reference 1. Model in confident standing pose, white background, editorial fashion lighting." dress_ref.jpg color_palette.jpg --input-fidelity high

# Using Google for multiple color options
imggen -p "
Design (first image): This dress silhouette and fit.
Color inspiration (second image): This jewel tone color palette.
Scene: Fashion photography on white background, professional studio lighting, dress on model with confident standing pose, editorial fashion quality." dress_ref.jpg color_palette.jpg --model gemini-3-pro-image-preview
```

## Prompting Tips

### What Works Well

✓ **Specific descriptions** - "sitting in wooden chair" beats "sitting"
✓ **Explicit constraints** - "preserve facial features" makes identity preservation a priority
✓ **Role indexing** - "Person 1 (first image)" removes ambiguity
✓ **Context** - Lighting, setting, atmosphere guides consistent output
✓ **Consistent terminology** - "the subject", "Person 1", "product" used consistently

### What Doesn't Work Well

✗ **Ambiguous pronouns** - "change it" without clear referent
✗ **Conflicting constraints** - "preserve pose exactly" AND "dynamic action pose"
✗ **Implicit references** - Assuming model knows which image is which without indexing
✗ **Over-specific pixel details** - "exact shade of blue in upper left corner" (models approximate)
✗ **Negations as main instruction** - "don't change the face" (describe what should happen instead)

### Fine-Tuning Output

If the output doesn't match expectations:

1. **More explicit constraints**: Add specific details to protect
2. **Clearer role assignment**: Use explicit indexing and naming
3. **Better context**: Include lighting, mood, style descriptors
4. **Try alternative wordings**: Different prompt structures sometimes resonate better
5. **Consider input_fidelity level**: High preserves identity, low allows reinterpretation (OpenAI)
6. **Simplify requests**: Complex multi-change prompts are harder to execute accurately

## Reference Images at Scale

### Dry Run for Cost Estimation

```bash
# See estimated cost without API calls
imggen -p "Change pose to sitting" person.jpg --variations 4 --dry-run
```

### Multiple Variations from One Reference

```bash
# Generate 4 different interpretations
imggen -p "Change background to different landscapes" landscape.jpg --variations 4 --output ./variations/
```

Each variation attempts the prompt independently, giving different creative interpretations.

## Troubleshooting

**Identity not preserved (OpenAI)**
- Try higher `input_fidelity` (use "high" explicitly)
- Make prompt more explicit: "preserve facial identity exactly"
- Reduce pose change magnitude
- Check image quality (very small/poor quality images are harder)

**Not using reference correctly (Google)**
- Add explicit indexing: "Person 1 (first image):", "Person 2 (second image):"
- Verify role descriptions match your intention
- Add more context about positioning and relationships
- Limit to necessary references (too many can confuse)

**File not found errors**
- Verify file paths are correct
- Use absolute paths or ensure files are in current directory
- Check file permissions (should be readable)

**Unexpected composition (either provider)**
- Simplify prompt structure
- Add explicit constraints
- Reduce number of simultaneous changes
- Use clearer positioning language
