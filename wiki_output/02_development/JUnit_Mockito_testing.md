---
title: "JUnit Mockito testing"
---

# JUnit Mockito testing

Below there is a **boilerplate unit test structure** using actual class names, and then a **practical explanation** of the annotations (`@RunWith`, `@Mock`, `@InjectMocks`, `@Spy`, `@Before`, `@Test`) — exactly how and when **Reportnet 3** uses them.

The versions in current use: 

  * JUnit 4
  * Mockito 3.11.2



* * *

[Edit this section](JUnit_Mockito_testing/edit.md)

## Cheatsheet

Mistake  | Why it’s Wrong  | Correct Usage  
---|---|---  
Using both `@RunWith(MockitoJUnitRunner.class)` **and** `MockitoAnnotations.openMocks(this)` | Both initialize mocks. Doing both causes redundant setup or conflicting mock states.  |  **Pick one:**  
• For **JUnit 4** , use `@RunWith(MockitoJUnitRunner.class)`.  
• For **manual initialization** (e.g. in abstract test classes), remove the runner and call `MockitoAnnotations.openMocks(this)` in `@Before`.   
Spying complex dependencies with `@Spy` |  `@Spy` calls real methods — can hit DB, APIs, or external systems unintentionally.  |  Use `@Mock` for dependencies. Reserve `@Spy` only for partial testing of **your own service methods** , not repositories or controllers.   
Mocking data objects (`VO`, `DTO`, or simple POJOs)  | Mocked DTOs return `null` or default values → assertions fail or lose real behavior.  |  Always use real instances:  
`DataSetSchemaVO schema = new DataSetSchemaVO();`  
Over-stubbing unused methods  | Unused stubs add noise and can trigger `UnnecessaryStubbingException` with strict mode.  |  Only stub what’s called in the test.  
`when(repo.findById("id")).thenReturn(Optional.of(...));`  
2/. Using `@InjectMocks` with a manually created instance (`new MyService()`)  | Mockito can’t inject mocks into pre-created objects — injection silently fails.  |  Let Mockito create it:  
`@InjectMocks private MyService myService;`  
Forgetting static/thread context setup (e.g. `SecurityContextHolder`)  | Missing context causes `NullPointerException` or inconsistent behavior in security-dependent logic.  |  In `@Before`:  
`SecurityContext context = mock(SecurityContext.class);`  
`SecurityContextHolder.setContext(context);`  
`ThreadPropertiesManager.setVariable("user", "user");`  
Verifying implementation details (e.g. `Mockito.verify(repo).findById(...)`)  | Brittle tests that fail after harmless refactors.  |  Verify observable behavior only:  
`assertEquals(expected, service.getById("123"));`  
Mixing `@Mock` and `@Spy` for dependencies  |  Partial mocks mix real logic and stubs → unpredictable results.  |  Choose one: use `@Mock` for isolation or real instance for integration-style tests. Never both.   
Forgetting to clear static context after tests  | Context leaks to other tests, causing non-deterministic failures.  |  In `@After`:  
`SecurityContextHolder.clearContext();`  
`ThreadPropertiesManager.remove();`  
  
* * *

[Edit this section](JUnit_Mockito_testing/edit.md)

## 🧪 Unit Testing Boilerplate (Mockito + JUnit)

Below is the standard structure for unit tests in our codebase.  
We use **JUnit 4** as the test framework and **Mockito 3.11.2** for mocking dependencies.

> Mind that the imports used are important, thus why they are included in codeblocks
[code] 
    package org.eea.dataset.service;
    
    import org.eea.dataset.persistence.schemas.repository.SchemasRepository;
    //[OTHER IMPORTS]
    import org.junit.Before;
    import org.junit.Test;
    import org.junit.runner.RunWith;
    import org.mockito.InjectMocks;
    import org.mockito.Mock;
    import org.mockito.Mockito;
    import org.mockito.MockitoAnnotations;
    import org.mockito.junit.MockitoJUnitRunner;
    
    import static org.junit.Assert.assertEquals;
    import static org.mockito.ArgumentMatchers.any;
    import static org.mockito.Mockito.when;
    
    @RunWith(MockitoJUnitRunner.class)
    public class DatasetSchemaServiceTest {
    
        @Mock
        private SchemasRepository schemasRepository;
    
        @Mock
        private DataSchemaMapper dataSchemaMapper;
    
        @InjectMocks
        private DataschemaServiceImpl dataSchemaServiceImpl;
    
        @Before
        public void initMocks() {
            MockitoAnnotations.openMocks(this);
        }
    
        @Test
        public void testFindDataSchemaById() {
            DataSetSchema schema = new DataSetSchema();
            DataSetSchemaVO schemaVO = new DataSetSchemaVO();
    
            Mockito.when(schemasRepository.findById(any())).thenReturn(Optional.of(schema));
            Mockito.when(dataSchemaMapper.entityToClass(schema)).thenReturn(schemaVO);
    
            DataSetSchemaVO result = dataSchemaServiceImpl.getDataSchemaById("5ce524fad31fc52540abae73");
    
            Assert.assertEquals(schemaVO, result);
        }
    }
    
[/code]

* * *

[Edit this section](JUnit_Mockito_testing/edit.md)

## ⚙️ Annotations Overview

Here’s how and **why** each annotation is used in our own test classes.

* * *

[Edit this section](JUnit_Mockito_testing/edit.md)

### `@RunWith(MockitoJUnitRunner.class)`

Used at **class level** to enable Mockito’s integration with JUnit 4.  
This runner automatically initializes fields annotated with `@Mock`, `@Spy`, and `@InjectMocks`.

We use it in every service test, for example:
[code] 
    @RunWith(MockitoJUnitRunner.class)
    public class DatasetSchemaServiceTest {
    
[/code]

→ This ensures that mocks like `schemasRepository` and `dataSchemaMapper` are created before tests run.

* * *

[Edit this section](JUnit_Mockito_testing/edit.md)

### `@Mock`

Creates a **Mockito mock** of a dependency.  
It replaces real implementations with dummy objects that can be controlled via `Mockito.when(...).thenReturn(...)`.
[code] 
    @Mock
    private SchemasRepository schemasRepository;
    @Mock
    private DataSchemaMapper dataSchemaMapper;
    
[/code]

→ These mocks isolate `DataschemaServiceImpl` from the database and mapping layer.  
→ Use `@Mock` for **repositories** , **controllers** , or **any external dependency** that you don’t want to execute real logic for.

* * *

[Edit this section](JUnit_Mockito_testing/edit.md)

### `@InjectMocks`

Creates an instance of the class under test and **injects** all `@Mock` (and `@Spy`) dependencies into it.
[code] 
    @InjectMocks
    private DataschemaServiceImpl dataSchemaServiceImpl;
    
[/code]

→ Mockito automatically injects all the mocks (`schemasRepository`, `dataSchemaMapper`, etc.) into `dataSchemaServiceImpl`.  
→ Use `@InjectMocks` for the **main class being tested** — typically a service class.

* * *

[Edit this section](JUnit_Mockito_testing/edit.md)

### `@Spy`

Creates a **partial mock** — it uses the real implementation but allows you to override or verify specific methods.
[code] 
    @Spy
    private List<ValidationSchemaCommand> validationCommands = new ArrayList<>();
    
[/code]

→ We use this when we need to keep real behavior (like a list’s behavior) but still verify interactions.  
→ Use `@Spy` when you want to test **real logic** , but still control or verify method calls.

Real use:  

[code]
      @Spy
      private List<ValidationSchemaCommand> validationCommands = new ArrayList<>();
    
      @Mock
      private ValidationSchemaIntegrityCommand command;
    
      @Before
      public void initMocks() {
        MockitoAnnotations.openMocks(this);
        validationCommands.add(command);
      }
    
    
[/code]

Ensures that when this command runs is partially mocked so it can be used by the test context.

* * *

[Edit this section](JUnit_Mockito_testing/edit.md)

### `@Before`

Marks a method that runs **before each test**.  
Used for setting up common state, initializing mocks, or configuring thread-local data.
[code] 
    @Before
    public void initMocks() {
        MockitoAnnotations.openMocks(this);
    }
    
[/code]

→ Ensures that Mockito initializes all mocks before tests run.  
→ We also use it to set up security context or thread variables when needed.

Real use:  

[code]
      @Before
      public void initMocks() {
    
        authentication = Mockito.mock(Authentication.class);
        securityContext = Mockito.mock(SecurityContext.class);
        securityContext.setAuthentication(authentication);
        SecurityContextHolder.setContext(securityContext);
    
        ThreadPropertiesManager.setVariable("user", "user");
    
        MockitoAnnotations.openMocks(this);
        validationCommands.add(command);
      }
    
[/code]

We setup the things that are going to be repeatetly used in test cases and we want to initialize them once. That could also include setting up dataflows, datasets and other stuff and changing only what is necessary inside each test to avoid code repetition and having more error prune tests.

* * *

[Edit this section](JUnit_Mockito_testing/edit.md)

### `@Test`

Marks a method as a **unit test**.  
Each `@Test` method should verify **one specific behavior** of the class under test. Select naming of class carefully because it will be shown at the test phase, it should be explicit. Do not care if it is long.
[code] 
    @Test
    public void testFindDataSchemaById() { ... }
    
[/code]

→ This test validates that `DataschemaServiceImpl.getDataSchemaById()` correctly maps and returns the schema object.

* * *

[Edit this section](JUnit_Mockito_testing/edit.md)

### Common Example of Mock Setup
[code] 
    Mockito.when(schemasRepository.findById(any())).thenReturn(Optional.of(schema));
    Mockito.when(dataSchemaMapper.entityToClass(schema)).thenReturn(schemaVO);
    
[/code]

→ These two lines define the mock behavior — they simulate repository and mapper responses so that the test focuses only on service logic.

* * *

[Edit this section](JUnit_Mockito_testing/edit.md)

## ⚠️ Common Annotation Misuse and Testing Pitfalls

Mockito annotations make tests cleaner, but **when used wrong** , they can make tests unstable, redundant, or misleading.  
Below are the most common mistakes we see — and what to do instead.

* * *

[Edit this section](JUnit_Mockito_testing/edit.md)

###  `@Mock` vs `@Spy` Confusion

**Misconception:**  
Developers sometimes think a `@Spy` is just a `@Mock` that calls real methods.  
In practice, spies are **real objects** wrapped with a Mockito proxy — meaning any method not explicitly stubbed **will execute real logic**.

**Wrong usage:**
[code] 
    @Spy
    private MyRepository repo = new MyRepository(); // This will call real DB code, do not ever use for repositories
    
[/code]

**Correct usage:**

  * Use `@Mock` for external dependencies or anything with side effects.
  * Use `@Spy` **only** for lightweight collaborators or lists/maps where real behavior is needed but some methods will be verified.



**Rule of thumb:**  
If the real object has dependencies, IO, or context — **never spy it**.

* * *

[Edit this section](JUnit_Mockito_testing/edit.md)

###  `@InjectMocks` Does Not Create Mocks

**Misconception:**  
Some devs assume `@InjectMocks` automatically creates mocks for all dependencies of the class.  
It doesn’t — it only **injects existing mocks/spies** into the tested class.

**Wrong usage:**
[code] 
    @InjectMocks
    private DataschemaServiceImpl dataSchemaServiceImpl;
    // but forgot to @Mock the repositories and rest of private fields
    
[/code]

→ The service will end up with `null` dependencies.

**Correct usage:**
[code] 
    @Mock private SchemasRepository schemasRepository;
    @Mock private DataSchemaMapper dataSchemaMapper;
    @InjectMocks private DataschemaServiceImpl dataSchemaServiceImpl;
    
[/code]

* * *

[Edit this section](JUnit_Mockito_testing/edit.md)

###  `MockitoAnnotations.openMocks(this)` vs `@RunWith(MockitoJUnitRunner.class)`

**Misconception:**  
Using both is redundant. Some tests initialize mocks twice — one via `@RunWith(MockitoJUnitRunner.class)` and another via `MockitoAnnotations.openMocks(this)` inside `@Before`.

**Wrong:**
[code] 
    @RunWith(MockitoJUnitRunner.class)
    public class MyTest {
      @Before
      public void setup() {
        MockitoAnnotations.openMocks(this); // unnecessary
      }
    }
    
[/code]

**Correct:**

  * If you use `@RunWith(MockitoJUnitRunner.class)`, it handles initialization.
  * Only call `MockitoAnnotations.openMocks(this)` when you **don’t use a runner** , e.g. in parameterized or Spring-based tests.



* * *

[Edit this section](JUnit_Mockito_testing/edit.md)

###  Over-stubbing (Unnecessary `when(...)`)

**Misconception:**  
Every dependency must be stubbed.  
You don’t need to stub methods that aren’t used by the method under test.

**Wrong:**
[code] 
    when(schemasRepository.findById(any())).thenReturn(Optional.of(...));
    when(dataSchemaMapper.entityToClass(any())).thenReturn(...);
    when(rulesRepository.findAll()).thenReturn(List.of()); // Not even used!
    
[/code]

→ Makes tests brittle — any unused stubs are misleading and will fail with `UnnecessaryStubbingException` in strict mode (at Jenkins).

**Correct:**  
Stub **only what your method under test actually calls**.

* * *

[Edit this section](JUnit_Mockito_testing/edit.md)

###  Mixing Real Logic and Mocks

**Misconception:**  
Injecting partial real objects alongside mocks is fine.  
In reality, this often breaks test isolation and causes unpredictable behavior.

**Wrong:**
[code] 
    @InjectMocks
    private DataschemaServiceImpl service = new DataschemaServiceImpl();
    @Mock private SchemasRepository repo;
    
[/code]

→ Mockito will try to inject mocks **and** you’re manually instantiating the same class — which breaks the injection process.

**Correct:**  
Let Mockito create the instance:
[code] 
    @InjectMocks
    private DataschemaServiceImpl service;
    
[/code]

* * *

[Edit this section](JUnit_Mockito_testing/edit.md)

###  Using `@Mock` for Value Objects (VOs)

**Misconception:**  
Mock everything!  
No, you don’t mock data carriers (VOs, DTOs, simple models). Mocking them prevents you from testing real serialization or mapper logic.

**Wrong:**
[code] 
    @Mock private DataSetSchemaVO schemaVO;
    
[/code]

**Correct:**
[code] 
    DataSetSchemaVO schemaVO = new DataSetSchemaVO();
    
[/code]

→ Only mock **behavioral** dependencies — never dumb data objects.

* * *

[Edit this section](JUnit_Mockito_testing/edit.md)

###  Verifying Internal Calls Instead of Output

**Misconception:**  
Verification (`Mockito.verify(...)`) is a must.  
Actually, verifying internal repository calls is an **implementation detail**.  
Prefer asserting **results** over verifying how they’re achieved.

**Wrong:**
[code] 
    Mockito.verify(schemasRepository).findById("5ce524...");
    
[/code]

**Correct:**
[code] 
    DataSetSchemaVO result = service.getDataSchemaById("5ce524...");
    assertEquals(expectedSchema, result);
    
[/code]

→ Use `Mockito.verify(...)` only when the behavior **is the outcome** , e.g. a Kafka message sent, a repository method triggered, or a command executed.

* * *

[Edit this section](JUnit_Mockito_testing/edit.md)

###  Forgetting `SecurityContext` or Thread Setup

In our codebase (`DatasetSchemaServiceTest`), some methods depend on `SecurityContextHolder` or `ThreadPropertiesManager`.  
If not initialized, tests will silently fail or behave inconsistently.

**Fix:**
[code] 
    @Before
    public void setup() {
        Authentication auth = mock(Authentication.class);
        SecurityContext context = mock(SecurityContext.class);
        when(context.getAuthentication()).thenReturn(auth);
        SecurityContextHolder.setContext(context);
        ThreadPropertiesManager.setVariable("user", "user");
    }
    
[/code]

Always re-initialize in `@Before`, not inside each test.

* * *

[Edit this section](JUnit_Mockito_testing/edit.md)

###  Forgetting Cleanup (`SecurityContextHolder.clearContext()`)

If you manipulate static/thread-bound contexts in tests (like `SecurityContextHolder`), always **reset them** afterward, especially in parameterized or suite runs.

**Tip:**
[code] 
    @After
    public void tearDown() {
        SecurityContextHolder.clearContext();
    }
    
[/code]

* * *

[Edit this section](JUnit_Mockito_testing/edit.md)

###  Verifying Too Much or Not Enough

**Over-verification** :
[code] 
    Mockito.verify(repo, times(1)).save(any());
    Mockito.verify(repo, times(1)).findById(any());
    Mockito.verify(repo, times(1)).delete(any());
    
[/code]

→ If our test only cares about `save()`, the rest is noise.

**Under-verification** :  
When a void interaction is critical (like `kafkaSenderUtils.releaseLock()`), not verifying it means missing a real regression.

## Verification notes

The framework versions stated (JUnit 4 and Mockito 3.11.2) are confirmed. Mockito version `3.11.2` is declared as `mockito.version` in `parent-poms/microservice/pom.xml`. Actual test files use `org.junit.runner.RunWith` and `org.junit.Test` imports (JUnit 4 APIs), as seen in `DatasetControllerImplTest.java` and `DatasetSchemaServiceTest.java`.

The class names used in the boilerplate example (`DataschemaServiceImpl`, `SchemasRepository`, `DataSchemaMapper`, `DataSetSchemaVO`, `DataSetSchema`) are real classes in the codebase. `DataschemaServiceImpl` exists at `dataset-service/src/main/java/org/eea/dataset/service/impl/DataschemaServiceImpl.java`. `DatasetSchemaServiceTest` exists at `dataset-service/src/test/java/org/eea/dataset/service/DatasetSchemaServiceTest.java`.

One inconsistency: the boilerplate cheatsheet at the top of the page correctly flags the combination of `@RunWith(MockitoJUnitRunner.class)` and `MockitoAnnotations.openMocks(this)` as a mistake. However, the boilerplate code block immediately below demonstrates this exact mistake: it uses `@RunWith(MockitoJUnitRunner.class)` at class level and calls `MockitoAnnotations.openMocks(this)` inside `@Before`. The real `DatasetSchemaServiceTest` in the source also does both. The page itself documents the pattern as wrong while showing it as correct; this should be resolved.

The page mentions emojis in section headings (the test tube and gear icons), which is inconsistent with the project documentation style guide.
