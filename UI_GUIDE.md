# UI Changes - Search Mode Toggle

## New Header Design

```
┌─────────────────────────────────────────────────────────────────┐
│  DA2 Listings                                                    │
│                                                                   │
│  ┌──────────────────┐  ┌──────────┐  ┌────────┐  ┌────────┐    │
│  │ Search...        │  │ ○──○     │  │ Search │  │ Home   │    │
│  │                  │  │ Smart    │  └────────┘  │ Create │    │
│  └──────────────────┘  └──────────┘              │ Logout │    │
│                         ^                         └────────┘    │
│                         Toggle Switch                            │
└─────────────────────────────────────────────────────────────────┘
```

## Toggle States

### Smart Search (ON) - Default
```
Search bar: [Smart search (e.g., 'Apple Phone')...]
Toggle:     [🧠 Smart Search]  ●──○
            ^^^^^^^^^^^^^^     ^^^^^
            Blue background    Switch ON
```

**Features:**
- Uses hybrid search (text + semantic)
- Understands synonyms and related terms
- Handles typos better
- Example: "Apple Phone" finds "iPhone"

### Keyword Search (OFF)
```
Search bar: [Keyword search...]
Toggle:     [🔍 Keyword Search]  ○──●
            ^^^^^^^^^^^^^^^^      ^^^^^
            Gray background      Switch OFF
```

**Features:**
- Uses text-only search
- Exact keyword matching
- Faster but less intelligent
- Example: "Apple Phone" only finds listings with those exact words

## Search Results Page

### With Smart Search
```
┌─────────────────────────────────────────────────────────────┐
│  Search Results                                              │
│  Searching for: Apple Phone  [🧠 Smart Search (understands  │
│                               synonyms)]                     │
│                                                              │
│  Found 1 listing                                            │
│                                                              │
│  ┌───────────────────────────────────────────────────────┐ │
│  │ [Image]                                               │ │
│  │                                                       │ │
│  │ iPhone                                          $100  │ │
│  │ iPhone 13                                            │ │
│  │                                                       │ │
│  │ 📍 Colombo  📂 electronics                           │ │
│  │ [smartphone] [apple] [iphone]                        │ │
│  │                                                       │ │
│  │ Relevance: 78%  ← Shows how well it matched         │ │
│  └───────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

### With Keyword Search
```
┌─────────────────────────────────────────────────────────────┐
│  Search Results                                              │
│  Searching for: iphone  [🔍 Keyword Search (exact matches)] │
│                                                              │
│  Found 1 listing                                            │
│                                                              │
│  ┌───────────────────────────────────────────────────────┐ │
│  │ [Image]                                               │ │
│  │                                                       │ │
│  │ iPhone                                          $100  │ │
│  │ iPhone 13                                            │ │
│  │                                                       │ │
│  │ 📍 Colombo  📂 electronics                           │ │
│  │ [smartphone] [apple] [iphone]                        │ │
│  └───────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

## User Flow Example

### Scenario: User wants to find an iPhone

#### Option 1: Smart Search (Recommended)
```
1. User types: "Apple Phone" in search bar
2. Toggle is ON (🧠 Smart Search)
3. Clicks "Search"
4. URL: /search?q=Apple+Phone&mode=smart
5. Backend receives: 
   - Original query: "Apple Phone"
   - Expanded to: "Apple Phone | iphone | ios phone | apple smartphone"
6. Result: iPhone listing with 78% relevance score ✅
```

#### Option 2: Keyword Search
```
1. User types: "Apple Phone" in search bar
2. User turns toggle OFF (🔍 Keyword Search)
3. Clicks "Search"
4. URL: /search?q=Apple+Phone&mode=keyword
5. Backend searches for literal words "Apple" and "Phone"
6. Result: May not find iPhone if it doesn't have exact words ❌
```

#### Option 3: Keyword Search with Exact Terms
```
1. User types: "iphone" in search bar
2. Toggle is OFF (🔍 Keyword Search)
3. Clicks "Search"
4. URL: /search?q=iphone&mode=keyword
5. Backend searches for literal word "iphone"
6. Result: iPhone listing found ✅
```

## CSS Implementation

The toggle switch is styled with smooth animations:

```css
.toggle-slider {
  width: 44px;
  height: 24px;
  background: gray;
  border-radius: 24px;
  transition: 0.3s;
}

/* When checked */
.toggle-checkbox:checked + .toggle-slider {
  background: blue; /* Primary color */
}

/* Sliding circle */
.toggle-slider::before {
  width: 18px;
  height: 18px;
  background: white;
  transform: translateX(0px);  /* OFF position */
}

.toggle-checkbox:checked + .toggle-slider::before {
  transform: translateX(20px); /* ON position */
}
```

## Accessibility

- ✅ Keyboard navigable (Tab to focus, Space to toggle)
- ✅ Screen reader friendly (label describes state)
- ✅ Clear visual feedback (color change + position change)
- ✅ Tooltip/placeholder hints at functionality

## Mobile Responsive

On smaller screens, the toggle may wrap to a new line:

```
┌────────────────────────────┐
│  DA2 Listings              │
│                            │
│  ┌──────────────────────┐ │
│  │ Search...            │ │
│  └──────────────────────┘ │
│                            │
│  ┌──────────┐  ┌────────┐ │
│  │ ○──○     │  │ Search │ │
│  │ Smart    │  └────────┘ │
│  └──────────┘             │
│                            │
│  [Home] [Create] [Logout] │
└────────────────────────────┘
```

## Best Practices

1. **Default to Smart Search** - Most users want intelligent matching
2. **Clear labeling** - Icons (🧠/🔍) make it immediately obvious
3. **Persistent state** - Mode is saved in URL, shareable
4. **Fallback handling** - If smart search fails, automatically tries keyword
5. **Visual feedback** - Badge on results page shows which mode was used
