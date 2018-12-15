
# Formal logic
I've taken [an introductory course on logic from Microsoft](https://courses.edx.org/courses/course-v1:Microsoft+DEV262x+1T2018a/course/) since I think it'll help me to improve as a programmer. Even if we see this type of things constantly around in our programming career, it is still quite helpful to know the academic side of it. With it, we'll be able to see a new side around how we build our programs with the integration of original concepts such as formal logic that are built around it. 

We may even utilize logic outside of programming and academics. This can be certainly be useful for analyzing real-life arguments and constructive sound arguments.

First, let's get into the formal introductions.

## What is logic
**Logic is a science of relationship between the statements and the conclusion.** The object of study within this domain is mostly the *reasonings* of the *argument*. It is simply examining the arguments with a critical eye and dealing with the reasonings of an argument. Viewing it with a critical eye means that we are using our *critical thinking* skills but what does it mean, really, is we are judging it based on a *criteria*. 

Logic can be said to be a science of how to think in order properly. The rules which describes the correct way of placing arguments are called *syllogisms*. There are also studies on the incorrect way of placing arguments and reasonings which are known as *fallacies*.

Now, you may have heard of the word *argument* before to denote of a verbal fight: "Alice and Bob are in an argument again whether it is worth it to go to the mountains or not."

## Arguments and statements
**In logic, an argument contains our conclusion and relating statements to back up our claim.** It is the simplest unit to be studied with when it comes to logic. 

An argument is made of *statements*. **These statements are often the one that make up our premises and the conclusion.**

If you think about it, in an argument (as in a verbal debate), we are basically claiming a point (the conclusion) and we are backing it up with relating statements (the premises). The opposing side then finds the value of your argument and try it bring it down with their arguments.

Let's see a simple example:

- Charlie is a computer programmer.
- All computer programmers know how to use a computer.
- Therefore, Charlie knows how to use a computer.

This is an argument composed of three statements. Two of these are premises and one of them makes up a conclusion.

Usually, statements that make a conclusion start with conclusive words such as "therefore", "thus", and "ergo" but there are cases where conclusions are not worded in that way. Some of them may instead include a mathematical symbol of that denotes the statement being a conclusion ($\therefore$) and some of them do not include neither symbols nor conclusive words. This all depends on the structure and flow of the argument as well as our intuition.

The premises have a truth value that affects the truth value of the conclusion. However, there are cases wherein the premises does not affect the conclusion at all and usually ends up being as a messy argument to deal with.

Take this argument for example:

- The grass is green.
- The crayons have colored pigments.
- Therefore, the sky is blue.

It's a contrived example but we can intuitively tell that this argument is senseless. The premises are true and the conclusion is also true. However, the premises do not relate at all with the conclusion.

We can say that an argument is made up of different parts:

- premises which is composed of the reasonings and evidences behind the conclusion
- conclusion which is the point that we claim 
- logical relation between the premises and how they lead to the conculsion

Like many other things, there are poorly constructed arguments and there are arguments that are well-done. There are arguments that are structurally correct but logically wrong and there are arguments that are just structurally wrong. Here, in logic, we inspect the structure and content of an argument in separate form. 

![Parts of an argument]({{ 'assets/pictures/self-learning-series/november-2018/arguments-parts.png' | relative_url }})

The problem is how do we state whether or not this argument holds its claim.

## Propositions
Enter *propositions*. **Simply this is the meaning behind the statements**. These are the one that we can determine whether the statement is true or false. With the concept of propostions, we can distinguish the meaning and the statements that makes up to it.

A simple example could be the representation of numbers. If I shown you this character: $5$, most likely you would say that it is the number 5 but it isn't. It's numeral 5. 

There are many ways to represent the number $5$. We can draw 5 dashes or draw 5 asterisks. We could also just draw the numeral 5. I could represent the number 5 with a black ink. You could represent the number 5 with a red ink. They could represent the number 5 with a bunch of pixels on a screen. But they all point out to the same proposition: the number 5.

Another typical example of this would be a number of statements that are in different language but means the same:

- Today is your birthday.
- Hoy es tu cumpleanos.
- 今日はあなたの誕生日です。

No matter what language this is, it still denotes that this day is your birthday which is arguably true (or false) depending when you encountered this as a part of an argument. Here, we have three statements but one proposition.

We could also say the same with at least two sentences which is structurally different:

- Dave wrote these two novels last year.
- Last year, these two novels have been written by Dave.

With the proposition being Dave wrote two novels last year which is again, arguably true (or false). We have two statements but one proposition.

There are some rules that makes up what is a proposition and what is not. **Propositions can only be gotten from a declarative statement for claiming how things are.** Anything else is not possible since they don't assert something on why, how, or any related statements on something. 

With imperative statements, being a command like "Close the door." is lacking in a logical sense. We cannot assert a command in a logical argument. Either we obey or disobey but it doesn't mean anything.

With interrogative statements like "Who are you?" or "How much is that tractor over there?", it does not assert a valuable claim either.

Exclamatory statements such as "Ouch!" or "$#!7!" does not claim anything, it only expresses their own feelings.

The main takeaway with propositions is that it is something that we claim. The statements themselves are not the one that we mainly inspect but it doesn't mean that it isn't important. The way how we constructed our argument can affect how others may interpret it. For example, there is a simple statement about something and one that is rearranged with more complicated words:

- Burgers made from Eve's Diner are made up of dirty meat.
- Burgers made from Eve's Diner are made with contaminated meat.
- Contamination is present on the meat that is used as burgers on Eve's Diner.

![Parts of an argument with propositions]({{ 'assets/pictures/self-learning-series/november-2018/complete-argument-parts.png' | relative_url }})

## Truth values
We now know that arguments are made up of premises, conclusion, and logical relation. That the premises and conclusion are made up of statements which each of them represents a proposition. Next to be discussed is the truth value.

**Truth values refers to the truthiness or falsity of a proposition.**

The important thing to know about truth values is that a proposition can be only be true or false. It cannot be both and it cannot be neither. When you don't know the truth value of a proposition and in order to continue your analysis, assume that it is true.

Let's take one of the previously mentioned examples and see the truth values in each statement:

| Propositions                                              | Truth value
|               ---                                         |
| Manila is the capital of the Phillipines.                 | T
| All dogs are fish.                                        | F
| There are more than 15 person on the park plaza.          | ?

The first given proposition is always true (at the time of writing, anyway) and the second proposition is always false. 

The third proposition however have interesting cases since it depends. There is no specificity into it and depends on a lot of factors like the time and whether or not it has been used for an event. A simple solution to this is to be more specific.

Applying that into the given proposition, we could say "There are more than 15 person on the park plaza at the time of the festival that occured on November 5, 2018." then we could determine its truth value.

The truth value of a statement obviously affects the truth value of the conclusion. Let's take a simple argument for an example:

| Propositions                              | Truth value
|               ---                         |
| All fishes have gills.                    | T
| All humans have gills.                    | F
| Therefore, all humans are fishes.         | F

Obviously, this is false as certainly a lot of us don't have gills ~~(or do we?)~~. 

![Parts of an argument with truth values]({{ 'assets/pictures/self-learning-series/november-2018/complete-argument-parts-w-values.png' | relative_url }})

## Symbolization
Like mathematics, the subject of logic is overall abstract and does have some bits of studying patterns.

This is where symbolization is coming from. **Basically, this is a process wherein we convert statements into its symbolic form.** It is certainly useful so that we can focus more on its form and not get distracted by its contents.

As previously said, in mathematics, we usually represent numbers in formulas with a letter.

$$ a^2 + b^2 = c^2 $$

*The Pythagorean theorem*{: .caption}

We could plug any values and solve for the unknown, if possible.

Assuming $a$ is equal to 3 and $c$ is equal to 5, find the value of $b$.

- $ a^2 + b^2 = c^2 $
- $ 3^2 + b^2 = 5^2 $
- $ 9 + b^2 = 25 $
- $ 9 + b^2 - 9 = 25 - 9 $
- $ b^2 = 16 $
- $ \sqrt{b^2} = \sqrt{16} $
- $ b = 4 $

*Step-by-step solution of the problem*{: .caption}

Logic has a concept similar to representing values with symbols. 

Let's take the previous example:

- All human are thinking creatures.
- All living things are thinking creatures.
- Therefore, all humans are living things.

Assuming we have difficulties in recognizing the truth value, we can see a pattern in here. Let's convert them into its symbolized form:

Similar to how we would represent ceratin things with a single letter in algebra, let's represent each things with a single letter. Or in programming terms, letting variable to represent for them.

Let's represent $H$ as "humans", $T$ to replace the "thinking creatures", and $L$ as the "living things" part. 

Take note that we can take any representation as long as it does not conflict your workflow. We could represent the three parts with different letters but for the sake for easier discussion, let's just take the first letter of the notable words.

- All $H$ are $T$
- All $L$ are $T$
- Therefore, all $H$ are $L$.

On a further note, this is a valid form which means that the we could also plug in values other than "humans", "thinking creatures", and "living things".

The process of symbolizing parts into letters can be seen when studying about the common valid syllogisms. When going to a logic textbook or any logic referential materials, you could see the valid argument forms in symbolic form. 

Remember, the process of breaking down statements into symbols can be the key and a forefront tool in analyzing arguments.

## Logical operators
Logical operators are valuable in the world of logic just like how several operators are to mathematics. What are they exactly? 

We know that statements make up the premises and the conclusion (and overall, the argument). Statements may be composed of a simple sentence like "Apples are red objects" or "`foo-dogsquared` is an aspiring programmer" but we can combine them to make one truth value.

For example, "Apples are red object and (apples) are often found in markets". 

Another value that can be found with operators is that they help you separate statements for the analysis to go smoother.

Let's take [this statement](https://searchwindowsserver.techtarget.com/definition/computer) for an exercise:

- A computer is a device that accepts information (in the form of digitalized data) and manipulates it for some result based on a program on how the data is to be processed.

We can separate this one big statement into multiple simple statements:

- A computer is a device *AND* a computer accepts information (in the form of digitalized data) *AND* a computer manipulates the data for some result based on a program on how the data is to be processed

So now we have three simple statements:

- A computer is a device
- A computer accepts information (in the form of digitalized data)
- A computer manipulates the data for some result based on a program on how the data is to be processed

So how this can be useful?

Since we're into computer programming (just assuming if you aren't), we've most likely (almost impossible to miss, in fact) encountered these logical operators.

Let's cut into the chase, shall we?

### `NOT` operator
Or in formal logic terms, the *negation operator*. It inverts the truth value of whatever statement that is specified with.

The formal symbol for it is a tilde (~).

$$ \text{~}A $$

$$ \text{It is not the case that } A $$

*Symbolic representation of the usage*{: .caption}

Example:
- It is not the case that all dogs are ferocious animals.

The simple statement in here is: "All dogs are ferocious animals.". We just attached it with a key phrase that clearly indicates that this is a negation. 

Now, you might have asked why not just go with a shorter answer such as "Not all dogs are ferocious animals" or "No dogs are ferocious animals"?

It is only because that we need to make sure that the simple statement does not change. The first alternative is also a valid one, retaining the simple statement but it could be mistaken to mean something (it may be interpreted as "Some dogs are ferocious animals"). The second alternative changed the simple statement. Now we don't know if the simple statement has been negated or not, unless we know it has been negated in the first place, of course.

Technically, the answers given above are also acceptable but it might cause some confusion when say, you're analyzing more complex arguments.

Let's have some statements given with no context whatsoever. Could you identify which statements have been negated?

- No cats are cute.
- It is not the case that red apples taste better than Granny Smith apples.
- My multimeter is not broken.

The given solution might be more cumbersome but once you get the hang of it, you'll eventually get it why it has been given that way. Take note that we can change the suggested key phrase as long as it can clearly indicate that the statement has been negated. We could go for something like: "It is not true that..." or "It is unacceptable that..." but that doesn't sound right. "It is not true that all dogs are cute."? Yeah, that's already confusing.

In summary, the negation operator simply *negates* or inverts the truth value of statement.

| $x$ | $\text{~$x$}$ 
| --- |
|  T  |     F       
|  F  |     T

### `AND` operator
The second item on the list is the *conjunction operator* or in programming terms, the `AND` operator. The conjunction operator combines two simple statements to form a conjunction. Even if you aren't into programming, this should make an intuitive sense.

The formal symbol for the conjunction operator is an ambersand (&) or a dot ($\cdot$).

$$ A \text{ & } B $$

$$ A \text{ and } B $$

*Symbolic representation of the usage*{: .caption}

Example:
- Ferris has no multimeter and Gremlinda has no soldering tools.

The simple statements that have been combined with the conjunction operator is now called a *conjunct*. So, there are two conjuncts in the compound statement: "Ferris has no multimeter." and "Gremlinda has no soldering tools.". If either conjunct is false, then the whole statement is false.

Following that if we're to assume that Ferris does have a multimeter (which makes the statement false), then the entire statement is already false since we cannot say that both of them does not have the specified tools.

In summary, the conjunction operator produces a truth value of true only if both conjuncts are true.

| $x$ | $y$ | $\text{$x$ & $y$}$
| --- | --- |
|  T  |  T  |   T
|  T  |  F  |   F
|  F  |  T  |   F
|  F  |  F  |   F

### `OR` operator
Next is the *disjunction operator* also known as the `OR` operator. Similar to the conjunction operator, the disjunction operator connects at least two statement together.

Formal symbol for the operator is called a wedge ($\wedge$), looking just like the letter V.

$$ A \wedge B $$

$$ A \text{ or } B $$

*Symbolic representation of the usage*{: .caption}

This time, statements that are connected by the operator is now called a *disjunct*. If either disjunct is true then the whole statement is considered to be true. The compound statement will only be false if all disjuncts were false.

Let's just use the previous example and see how different it is from using a conjunction operator:
- Ferris has no multimeter or Gremlinda has no soldering tools.

Like the conjunction operator, it has two disjuncts: "Ferris has no multimeter" and "Gremlinda has no soldering tools". Say that Ferris did indeed has no multimeter, then we can say that the compound statement is indeed true.

What we're saying with the disjunction in this statement is that either Ferris or Gremlinda doesn't have the specified tools. So it would make intuitive sense that at least one of them is true means the whole statement is true.

In summary, in relation to the conjunction operator, the disjunction operator will produce a truth value of false only if all disjuncts were false.

| $x$ | $y$ | $x \wedge y$
| --- | --- |
|  T  |  T  |   T
|  T  |  F  |   T
|  F  |  T  |   T
|  F  |  F  |   F

### `IF-THEN` statement
Also known as the *conditional*. This is a logical operator that sets a condition and will be true when the condition has met.

Formal symbols for the conditional operator is an arrow ($\implies$) or a horseshoe ($\supset$).

$$ A \implies B $$

*Symbolic representation of the usage*{: .caption}

For verbal representation of the statement, it could look like this:

$$ \text{If $A$ then $B$} $$

Like most operators so far, statements connected by a conditional operator has its own term. The one on the left is called the *antecedent* with the Latin prefix ante-, meaning before. The statement on the right side of the operator is called the *consequent* because you know, of the word, consequences.

**Take note that conditionals themselves are not arguments. They can however take part of a premise.**

So let's try to make sense of the example given below:
- If Ferris has no multimeter then Gremlinda has no soldering tools.

In the example, the antecedent is "Ferris has no multimeter" and the consequent is "Gremlinda has no soldering tools". Take note that we are not including the `if` and `then` since they are a part of the operator. 

We cannot really produce a truth value of it unless we have premises that declare a proposition.

Now let's add a premise and a conclusion:
- If Ferris has no multimeter then Gremlinda has no soldering tools.
- Ferris has no multimeter.
- Therefore, Gremlinda has no soldering tools.

OK. Now we can imagine clearly about what are we trying to claim here.

First, we set up a condition through the conditional operator, no biggie. Then, we claimed that Ferris indeed has no multimeter which means Gremlinda has no soldering tools. 

Assuming Ferris did not have multimeter, we can say that the antecedent is true. Following that logic, Gremlinda should have no soldering tools. 

Then things are getting more confusing. Somewhat.

Look at this truth table for a minute:

| $x$ | $y$ | $x \implies y$
| --- | --- |
|  T  |  T  |   T
|  T  |  F  |   F
|  F  |  T  |   T
|  F  |  F  |   T

We can see that conditionals as a whole produces a truth value of false only if the antecedent is true and the consequent is false. If we invert the values with the antecedent is now false and the consequent is true, the conditional as a whole is true.

#### Why is that?
Simply speaking, the conditional's truth value is truth-functional based. What I mean is that you only care for the conditonal as a whole and whether or not the function has done its job.

For this, we shall have an analogy.

Let's say that you made a zipper alarm and put it on a bag. When the zipper has been pulled and opened the bag entirely, an alarm will set off. You might've noticed something about the previous statement being almost similar to a conditional. And yes, it does!

Take note of our little system here: when the zipper has been pulled and opened the bag entirely, an alarm will set off. As an engineer that testing out devices, that's all we care about. Anything else is not within our concern.

That is our function that will produce a truth value. I'm pretty sure you can tell that the antecedent here is "The zipper has been pulled and opened the bag entirely" and the consequent is "An alarm will set off".

Now that we have done the creation of a simple zipper alarm. Let's go through some testing with our chosen condition:

- Experiment #1: The zipper has been pulled halfway. (F)
- Result: The alarm did not set off. (F)
- Has the function failed? *No.* (T)

OK. We've pulled the zipper down halfway which means that it is false, in terms of truth value. The resulting event is that the alarm did not set off. In terms of our function, that is an A-OK signal. Our system (the chosen condition) did not fail.

- Experiment #2: The zipper has been pulled a third of the quarter of the bag before it's fully opened. (F)
- Result: The alarm did set off. (T)
- Has the function failed? *No.* (T)

Next experiment and it has set the alarm. However, it is from the zipper being pulled 75% before the bag is opened entirely. Has your function failed? No, because it did not came from the efforts that our bag is opened entirely. As a testing engineer, you don't care about that stuff. You only look after the results that came from the antecedent: when the bag is opened entirely. So no, our system did not fail.

- Experiment #3: The bag has been opened entirely. (T)
- Result: The alarm did not set off. (F)
- Has the function failed? *Yes.* (F)

Hmm... Now the function set off and the alarm... did not set off. This is a lie. Or a declaration that our function failed which means it's a false.

OK. So assuming that it did work, how about that?

- Hypothetical Experiment: The bag has been opened entirely. (T)
- Result: The alarm did make an annoying sound which means it sets off. (T)
- Has the function failed? *No. Congratulations!* (T)

Well, the bag is opened entirely and the alarm has set. Which means our function (or system) did not failed. 

Congratulations on your first job, imaginary testing engineer! Now test the other conditions for our zipper alarm.

## Source(s):
- [This Microsoft edX course on logic](https://courses.edx.org/courses/course-v1:Microsoft+DEV262x+1T2018a/course/)