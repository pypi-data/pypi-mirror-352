
# Game Simulator

This library analyzes strategy evolution in normal-form games, focusing on how various factors such as initial state, payoff values, memory length, randomness in decision-making, and response functions shape the path to final outcomes. By tracking agent interactions over time, it reveals the key transitions, identifying what drives strategic shifts and when they occur.
## How to use it?


```bash
  # Install
  pip install game-simulator
  
  # Import
  from game_simulator import simulation

  # Execute (first approach)
    simulation.simulation_function(num_rows=2,
                        num_cols=3,
                        memory_length=2,
                        iterate_all="YES",
                        initial_history=[[0,1],[1,1],[1,2]],
                        timeperiod=10,
                        iteration_name="test",
			random_seed=5879,
                        row_player_payoffs=[2,0,0,2,1,2],
                        column_player_payoffs=[1,2,1,3,2,2],
                        path_to_save_output="C:\\Users\\Downloads\\")
						
    simulation.simulation_function_random(num_rows=2,
                        num_cols=3,
                        memory_length=2,
                        iterate_all="YES",
                        initial_history=[[0,1],[1,1],[1,2]],
                        timeperiod=10,
                        iteration_name="test",
			random_multiplier=8,
                        random_seed=5879,
                        row_player_payoffs=[2,0,0,2,1,2],
                        column_player_payoffs=[1,2,1,3,2,2],
                        path_to_save_output="C:\\Users\\Downloads\\",
			time_period_randomness_reduce = None,
			percent_reduce_randomness=0.5,
			remove_randomness="No")

# Execute (second approach)
    simulation.simulation_function_payoff(num_rows=2,
                        num_cols=3,
                        memory_length=2,
                        iterate_all="YES",
                        initial_history=[[0,1],[1,1],[1,2]],
                        timeperiod=10,
                        iteration_name="test",
			random_seed=5879,
                        row_player_payoffs=[2,0,0,2,1,2],
                        column_player_payoffs=[1,2,1,3,2,2],
                        path_to_save_output="C:\\Users\\Downloads\\")
						
    simulation.simulation_function_payoff_random(num_rows=2,
                        num_cols=3,
                        memory_length=2,
                        iterate_all="YES",
                        initial_history=[[0,1],[1,1],[1,2]],
                        timeperiod=10,
                        iteration_name="test",
			random_multiplier=8,
                        random_seed=5879,
                        row_player_payoffs=[2,0,0,2,1,2],
                        column_player_payoffs=[1,2,1,3,2,2],
                        path_to_save_output="C:\\Users\\Downloads\\",
			time_period_randomness_reduce=None,
			percent_reduce_randomness=0.5,
			remove_randomness="No")
						
						
# Execute (generate graphs)

   simulation.function_to_generate_graphs(input_excel_file="timeperiodexcel.xlsx",
                               path_to_save_output="C:\\Users\\Downloads\\",
                               figure_name="figure1")
							   
							   
   simulation.function_to_generate_cumulative_graphs(input_excel_file="timeperiodexcel.xlsx",
                               path_to_save_output="C:\\Users\\Downloads\\",
                               figure_name="figure1")
							   

```
    
## Function parameters
The library has two functions, simulation_function and simulation_function_payoff. We have considered two different approaches which agents can potentially use to decide what strategy to choose at any given point during the game. In the first approach, agents take all possible histories into consideration while deciding the next course of action which is captured in simulation_function while in the second approach (simulation_function_payoff) agents compute their expected payoffs and choose the strategy having maximum payoff.
We have given a detailed explanation of these functions in the next two sections. 

Following are the parameters which are required to be specified. At the end in the parenthesis, it shows the data type of the parameter which is required or the possible values which is required to be used.

1.	num_rows : Number of rows in the payoff matrix. (Integer)
2.	num_cols : Number of columns in the payoff matrix. (Integer)
3.	memory_length : How much history need to consider. (Integer)
4.	iterate_all : Whether to consider all possible combinations of history or specific. ("YES" or "NO"). In case of "YES", the function computes all possible combinations of histories, and if the count of these potential histories is higher than 5, the function selects 5 histories randomly.
5.	initial_history : Valid when iterate_all = NO. A list of initial history. Specify as [[0,1], [1,2]]. This means the first period outcome is first strategy for row player and second strategy for column player. The second period outcome is second strategy for row player and 3rd strategy for column player. Please note these are the positions of the strategies in the payoff matrix, and not the payoff values. Here we have specified 2 period histories. Therefore, memory_length should be 2. (List)
6.	timeperiod: The timeperiod for which iterations are required to run? (Integer)
7.	iteration_name: Give any name for these iterations. (String)
8.	row_player_payoffs. List of row player payoffs. To be specified as first row payoff, second row payoffs, and so on E.g. [2,0,2,5] implies first row payoffs for row player are 2 and 0 against first and second strategy of the column player. Second row payoffs for row player are 2 and 5. This is assuming we have 2*2 payoff matrix. (List)
9.	column_player_payoffs. Same as row_player_payoffs. But this specifies the column player payoffs. (List)
10.	path_to_save_output. The location where output excel files should be saved. (String)
11. random_seed. Any random number. (Integer)
12. random_multiplier. The multiple by which non-random choices are weighted. In case of tradeoff between non-random and random choices, non-random choices are being weighted random_multiplier times higher than random choices. (Integer)
13. time_period_randomness_reduce. The time period when randomness is required to be reduced, meaning non-random choices would be weighted more from this period onwards. Default value is None,implying randomness stays constant throughout the game. (Integer)
14. percent_reduce_randomness. The multiple by which non-random choices would be weighted more. If time_period_randomness_reduce is not None, then random_multiplier would become (random_multiplier+random_multiplier*percent_reduce_randomness) from time_period_randomness_reduce onwards. Default value is 0.5. (float)
15. remove_randomness. A binary flag to indicate if randomness is required to be completely removed. If time_period_randomness_reduce is not None and remove_randomness = "Yes", then randomness is completely removed and only recommended/non-random choices are considered from time_period_randomness_reduce onwards. Default value is "No",implying randomness would not be completely removed. Possible values are either "Yes" or "No". 
16. input_excel_file. Specify the path of excel file with "timeperiod" keyword which gets generated by executing any of the 4 simulation functions. More details on the excel files generated are provided in sections below.
17. figure_name. Specify any name for the figure/graph. 


## Function explanation (simulation_function)
Consider the 2*2 game with following payoff values.

    (2,1)	(0,0)
    (0,0)	(1,2)


We assume the memory window as 2 periods. Suppose the initial 2 period history is (0,0) and (1,1). We denote (0,0) and (1,1) as the position of strategies and not the payoff. Therefore, (0,0) corresponds to (2,1) and (1,1) corresponds to (1,2) in the above payoff table. We assume that there are 2 agents playing the game at any given point in time and agents are indistinguishable. At the beginning of the game, there is no history available, so agents select action randomly.

At the beginning of period 3, row and column players evaluate what is played by the opponent in period 1 and period 2. In this case, row player thinks about best response against the column player playing 0 or 1 since both 0 and 1 strategy is being played by column player in period 1 and 2 respectively. Similarly, column player thinks about its best response against the row player playing 0 or 1 due to both strategies being played by row player in period 1 and 2 respectively.

As per the payoffs defined, if the column player plays 0, the best response for row player is to play 0. If the column player plays 1, the best response for row player is also to play 1. Similarly, if the row player plays 0, the best response for column player is to play 0 and if the row player plays 1, the best response for column player is also to play 1. Therefore, at the end of period 3 or beginning of period 4, we have following histories of periods 2 and 3, which will be available for players at the beginning of period 4.

Period 1: (0,0), selected randomly

Period 2: (1,1), selected randomly

Row/Column player choices in period 3:

1.	History available in period 3: (0,0), (1,1)

2.	Row player choices = 0,1

3.	Column player choices = 0,1

4.	Possible strategies available in period 3.

	    (0,0): both row and column player play 0
        (0,1): row player plays 0 and column player plays 1
        (1,0): row player plays 1 and column player plays 0
        (1,1): row player plays 1 and column player plays 1
Below are the potential histories available at beginning of period 4. This has been written as strategies in period 2 followed by strategies in period 3.

    (1,1), (0,0)
    (1,1), (0,1)
    (1,1), (1,0)
    (1,1), (1,1)

Therefore, there are potential 4 histories available at the beginning of period 4 depending upon what strategies row or column players select in period 3. Histories in period 4 denote choices made in period 2 followed by period 3. 

At the end of timeperiod, we take the frequency count of different possible combinations across all the time periods considered. In the 2*2 matrix framework, there could be 4 possible strategy combinations namely (0,0), (0,1), (1,0) and (1,1). Depending upon the initial history selected, the percentage distribution of these strategy pairs varies. The strategy pairs which occurred more frequently relative to others are indicative of potential candidates for norms. We also investigate the trend of different strategy pairs over the period to check if any specific strategy pair trends upwards or downwards. The strategy pair trending upwards over a period is indicative of potential norm.

The other function "simulation_function_random" works same as this function except that it allows agents to take decisions randomly with the weight parameter "random_multiplier". Non-random choices are being weighted random_multiplier times higher than random choices. Use this parameter along side other parameters which control randomness like, "time_period_randomness_reduce", "percent_reduce_randomness" and "remove_randomness".





## Function explanation (simulation_function_payoff)
In the second approach, we calculate the expected payoff of row/column players against different strategies. Agents choose the strategy which is having higher expected payoff values. Consider the below 2*2 game with same payoff matrix as in first approach.

    (2,1)	(0,0)
    (0,0)	(1,2)

Suppose the initial 2 period history is (0,0) and (1,1). Here both row and column player has played 0 and 1 once. For players to decide which strategy to choose in the next period, expected payoffs are computed for both row and column players against different strategies.

Expected payoff of row player when playing strategy 0 equals  (1/2) * 2 + (1/2) * 0 = 1. This is computed using the first row from the above matrix (row player payoffs) multiplied by the weights. These weights are derived from row player"s expectations about column player playing 0 or 1 strategy. Since by assumption 2 periods of history is considered and column player has played 0 and 1 once in these 2 periods, hence the probability of column player playing 0 again in next period is (1/2). Similarly, the probability for column player playing strategy 1 is (1/2) . On the similar lines, column player also computes the row player"s expectations of playing 0 or 1 in the next period based upon the 2 period history. In this case, expected payoff of column player playing 0 = 1* (1/2) + 0 * (1/2)  = 0.5. This is first column of above matrix (column player payoffs) multiplied by the weights. Hence, we can create below matrix of expected payoffs.

    Strategy	Row player expected payoff	Column player expected payoff
    0	            2* (1/2) + 0* (1/2) = 1             1* (1/2) + 0 * (1/2)   = 0.5
    1	            0 * (1/2) + 1 * (1/2) = 0.5         0* (1/2) + 2* (1/2) = 1

Row player will play strategy 0 and column player will play strategy 1 as expected payoffs are higher corresponding to these strategies. Therefore, for period 3 strategies are (0, 1). At the beginning of period 4, the history would constitute period 2 and period 3 outcomes. Hence, (1,1) and (0,1) becomes the history input for period 4 strategies. The same process continues for rest of the periods. In case of a tie (exact expected payoffs for row / column player playing different strategies), both the strategies are considered for the next periods.

The other function "simulation_function_payoff_random" works same as this function except that it allows agents to take decisions randomly with the weight parameter "random_multiplier". Non-random choices are being weighted random_multiplier times higher than random choices.





## How to interpret output?
There will be 3 excel files which would get generated by running these functions
    
    all_iteration_data_timperiod_test_2022-06-28-17-09-37.xlsx
    all_iteration_data_test_2022-06-28-17-09-37.xlsx
    all_iteration_data_payoffmatrix_test_2022-06-28-17-09-37.xlsx

In case if the parameter iterate_all is set to "NO" in that case the file names would start with  selected_iteration_ like below.

    selected_iteration_data_payoffmatrix_test_2022-06-28-17-12-56.xlsx
    selected_iteration_data_timperiod_test_2022-06-28-17-12-56.xlsx
    selected_iteration_data_test_2022-06-28-17-12-56.xlsx

The interpretation for the "selected" files and "all" files are same except that "selected" files contain information about only those results against the initial history specified while "all" contain results against all the possible potential initial histories.

The format of these files starts with whether the results are for selected initial history, or all initial history followed by "data" (aggregated results across all time periods are in this file) or "data_timeperiod" (individual time period results are in this file), iteration_name and timestamp when the function was executed. The "data_payoffmatrix" file contains the information of payoff matrix which is specified in row_player_payoffs and column_player_payoffs.

Column "keys" in the excel contains the strategy position. "Count" or "count1" contains the percentage of times that particular strategy is being played. Column "initial_history" is the strategy positions with which the game started and "timeperiod" shows the incremental time period when the agents were in that state.


There will be 2 image files (jpeg) gets generated if we execute the graphs related function. "function_to_generate_graphs function" would generate graph with time period on X-axis and Count% on Y-axis. The Count % indicates the percentage of times, a specific action pair is being observed considering all prior history till that point in time. The sum of Count% across all potential strategy/action pairs at any given period equals 100. Below is sample output of Count% graph.

![](https://github.com/ankur-tutlani/game-simulator/raw/main/PercentCountgraph.png)

The second function, "function_to_generate_cumulative_graphs" generates cumulative graph. This shows the presence or absence of specific action pair at any given time period. If a specific action pair is being played during that period, its count gets incremented by 1. If that pair is not being observed in future period, the cumulative count stays the same for future time periods. Hence, the output of this graph is cumulative count of action pairs at each time period. This graph is useful in scenarios where we observe any one specific action pair is being played at any given time and we want to see how that is changing over time. Below is sample output of Cumulative Count graph.

![](https://github.com/ankur-tutlani/game-simulator/raw/main/CumulativeCountgraph.png)

Both these graphs functions would generate graphs considering a specific initial state. If the "timeperiod" excel contains results from multiple initial states, then there would be multiple graphs generated for each individual initial state. The specific initial state considered would be in the file name with _ after the figure name provided.


