import SudokuBoard
import Variable
import Domain
import Trail
import Constraint
import ConstraintNetwork
import time

class BTSolver:

    # ==================================================================
    # Constructors
    # ==================================================================

    def __init__ ( self, gb, trail, val_sh, var_sh, cc ):
        self.network = ConstraintNetwork.ConstraintNetwork(gb)
        self.hassolution = False
        self.gameboard = gb
        self.trail = trail

        self.varHeuristics = var_sh
        self.valHeuristics = val_sh
        self.cChecks = cc

    # ==================================================================
    # Consistency Checks
    # ==================================================================

    # Basic consistency check, no propagation done
    def assignmentsCheck ( self ):
        for c in self.network.getConstraints():
            if not c.isConsistent():
                return False
        return True

    """
        Part 1 TODO: Implement the Forward Checking Heuristic

        This function will do both Constraint Propagation and check
        the consistency of the network

        (1) If a variable is assigned then eliminate that value from
            the square's neighbors.

        Note: remember to trail.push variables before you change their domain
        Return: true is assignment is consistent, false otherwise
    """
    def forwardChecking ( self ):
        for node in self.network.variables:
            if node.isAssigned():
                current = node.domain.values[0]
                for neighbor in self.network.getNeighborsOfVariable(node):
                    if current in neighbor.domain.values:
                        self.trail.push(neighbor)
                        neighbor.removeValueFromDomain(current)

        return self.assignmentsCheck()

    """
        Part 2 TODO: Implement both of Norvig's Heuristics

        This function will do both Constraint Propagation and check
        the consistency of the network

        (1) If a variable is assigned then eliminate that value from
            the square's neighbors.

        (2) If a constraint has only one possible place for a value
            then put the value there.

        Note: remember to trail.push variables before you change their domain
        Return: true is assignment is consistent, false otherwise
    """
    def norvigCheck ( self ):
        for node in self.network.variables:
            if node.isAssigned():
                current = node.domain.values[0]
                for node2 in self.network.getNeighborsOfVariable(node):
                    if current in node2.domain.values:
                        self.trail.push(node2)
                        node2.removeValueFromDomain(current)
        for strain in self.network.constraints:
            result = []
            for i in range(self.gameboard.N):
                result.append(0)
            for v in strain.vars:
                if v.isAssigned():
                    continue
                else:
                    for x in v.domain.values:
                        result[x-1] == 1
            for i2 in range(self.gameboard.N):
                if result[i2] == 1:
                    for v in strain.vars:
                        if v.domain.contains(i2+1):
                            self.trail.push(v)
                            v.assignValue(i2+1) 
        return self.assignmentsCheck() 
    """
         Opti nal TODO: Implement your own advanced Constraint Propagation

         Completing the three tourn heuristic will automatically enter
         your program into a tournament.
     """
    def getTournCC ( self ):
        return None

    # ==================================================================
    # Variable Selectors
    # ==================================================================

    # Basic variable selector, returns first unassigned variable
    def getfirstUnassignedVariable ( self ):
        for v in self.network.variables:
            if not v.isAssigned():
                return v

        # Everything is assigned
        return None

    """
        Part 1 TODO: Implement the Minimum Remaining Value Heuristic

        Return: The unassigned variable with the smallest domain
    """
    def getMRV ( self ):
        smallest_domain = self.gameboard.N + 1
        var = None
        for v in self.network.variables:
            if not v.isAssigned() and v.size() < smallest_domain:
                smallest_domain = v.size()
                var = v

        return var

    """
        Part 2 TODO: Implement the Minimum Remaining Value Heuristic
                       with Degree Heuristic as a Tie Breaker

        Return: The unassigned variable with, first, the smallest domain
                and, second, the most unassigned neighbors
    """
    def MRVwithTieBreaker ( self ):
        min_remain = self.gameboard.N + 1
        tie = []
        current_m = None
        if self.getfirstUnassignedVariable() == None:
            return None
        for v in self.network.variables:
            if not v.isAssigned():
                if v.size() < min_remain:
                    min_remain = v.size()
                    current_m = v
                    tie = [v]
                elif v.size() == min_remain:
                    tie.append(v)
        d = dict()
        for v in tie:
             d[v] = 0
        for v in tie:
             neighbors = self.network.getNeighborsOfVariable(v)
             for n in neighbors:
                 if not n.isAssigned():
                     d[v] += 1
        keys =  sorted(d.keys(), key = d.get)
        return keys[0]

    """
         Optional TODO: Implement your own advanced Variable Heuristic

         Completing the three tourn heuristic will automatically enter
         your program into a tournament.
     """
    def getTournVar ( self ):
        return None

    # ==================================================================
    # Value Selectors
    # ==================================================================

    # Default Value Ordering
    def getValuesInOrder ( self, v ):
        values = v.domain.values
        return sorted( values )

    """
        Part 1 TODO: Implement the Least Constraining Value Heuristic

        The Least constraining value is the one that will knock the least
        values out of it's neighbors domain.

        Return: A list of v's domain sorted by the LCV heuristic
                The LCV is first and the MCV is last
    """
    def getValuesLCVOrder ( self, v ):
        lst = []
        tempdict = {}
        values = v.domain.values
        for i in values:
            cnt = 0
            for x in self.network.getNeighborsOfVariable(v):
                if i in x.getDomain().values:
                    cnt= cnt+1
            tempdict[i] = cnt
        for key, value in sorted(tempdict.items(), key = lambda u:u[1]):
            lst.append(key)
        return lst

    """
         Optional TODO: Implement your own advanced Value Heuristic

         Completing the three tourn heuristic will automatically enter
         your program into a tournament.
     """
    def getTournVal ( self, v ):
        return None

    # ==================================================================
    # Engine Functions
    # ==================================================================

    def solve ( self ):
        if self.hassolution:
            return

        # Variable Selection
        v = self.selectNextVariable()

        # check if the assigment is complete
        if ( v == None ):
            for var in self.network.variables:

                # If all variables haven't been assigned
                if not var.isAssigned():
                    print ( "Error" )

            # Success
            self.hassolution = True
            return

        # Attempt to assign a value
        for i in self.getNextValues( v ):

            # Store place in trail and push variable's state on trail
            self.trail.placeTrailMarker()
            self.trail.push( v )

            # Assign the value
            v.assignValue( i )

            # Propagate constraints, check consistency, recurse
            if self.checkConsistency():
                self.solve()

            # If this assignment succeeded, return
            if self.hassolution:
                return

            # Otherwise backtrack
            self.trail.undo()

    def checkConsistency ( self ):
        if self.cChecks == "forwardChecking":
            return self.forwardChecking()

        if self.cChecks == "norvigCheck":
            return self.norvigCheck()

        if self.cChecks == "tournCC":
            return self.getTournCC()

        else:
            return self.assignmentsCheck()

    def selectNextVariable ( self ):
        if self.varHeuristics == "MinimumRemainingValue":
            return self.getMRV()

        if self.varHeuristics == "MRVwithTieBreaker":
            return self.MRVwithTieBreaker()

        if self.varHeuristics == "tournVar":
            return self.getTournVar()

        else:
            return self.getfirstUnassignedVariable()

    def getNextValues ( self, v ):
        if self.valHeuristics == "LeastConstrainingValue":
            return self.getValuesLCVOrder( v )

        if self.valHeuristics == "tournVal":
            return self.getTournVal( v )

        else:
            return self.getValuesInOrder( v )

    def getSolution ( self ):
        return self.network.toSudokuBoard(self.gameboard.p, self.gameboard.q)
