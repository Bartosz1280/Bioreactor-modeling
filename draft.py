## THIS IS A DRAFT FILE THAT IS NOT PUSH TO THE REMOTE


class Equation:
    def __init__(self,equation: str):
        def fix_spacing(right_side_equation: str):
            """
            Sometimes an equation might be pased with 
            not coherent spacing, hindering proper str
            to equation conversion.
            To avoid these problems and make the code
            simpler be defualt each equations is passed
            into that function
            """
            # Defines mathematical symbols
            #
            # To be able to accept and process variaty of equations that 
            # not always follows python convention but also some other popular
            # formats to separate list of symbols represneting mathematical 
            # operations were diclared
            #
            # Universal and python specific operators
            #
            # For those symbols only the correct spacing is introduced,
            # since python can intepreted them directly
            universal_math_operators = [
                   "+" , "-" , "*","**",
                   "/",  "(" , ")" , "[","]"]
            # Iterates throught the equation
            # spliting the equation on mathematical
            # operators to rejoin them on correctly spaced operator
            #
            # Removes any spacing within the equation, to simplyfy 
            # the process
            right_side_equation = "".join(right_side_equation.split(" "))
            # Makes sure that power will not be mistook for multiplication
            right_side_equation = " ^ ".join(right_side_equation.split("**"))
            # First loop takes care of correct spacing for universal operators
            for i in universal_math_operators: # MIGHT REQUIRE SOME DEBUGGING !
                right_side_equation = f" {i} ".join(right_side_equation.split(i))
            right_side_equation = "**".join(right_side_equation.split("^"))
            
            return right_side_equation

        def cast_equation_to_python_str(equation: str):
                universal_math_operators = [
                   "+" , "-" , "*","**",
                   "/",  "(" , ")" , "[","]"]
                popular_math_operators=["^", "ln","log", "exp"]
                equation_list = equation.split(" ")
                for i in equation_list:
                    # Determienes if i is a numerical value
                    # If true just pass
                    try:
                        float(i)
                    # If false tries to determine if i is var/conts 
                    # or mathematical operation
                    except ValueError:
                        # Grabs mathematical operation to convert it 
                        # to python redable expression
                        if i in popular_math_operators:
                            match i:
                                case "^":
                                    equation_list[equation_list.index(i)] = "**"
                                case "ln":
                                    equation_list[equation_list.index(i)] = "math.ln"
                                case "log":
                                    equation_list[equation_list.index(i)] = "math.log"
                                case "exp":
                                    equation_list[equation_list.index(i)] = "math.exp"
                        # Remainig possiblity is that i is var/const
                        elif i not in universal_math_operators and i !="":
                            equation_list[equation_list.index(i)] = f"self.{i}"
                return "".join(equation_list)

Equation("x = c + z-2*f +log(n) + s**2")
