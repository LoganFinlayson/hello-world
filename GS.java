import java.util.*;

public class GS {

	private static int numTests, numPairs; //Number of tests and number of pairs.
	
	public static void main(String[] args) {
		Scanner keyboard = new Scanner(System.in);
		numTests = keyboard.nextInt();
		keyboard.useDelimiter("[ MW\r\n]+");
		
		keyboard.nextLine();
		//System.out.println("Number of tests: " + numTests);
		
		for (int i = 0; i < numTests; i++) {
			numPairs = keyboard.nextInt();
			//System.out.println("Number of pairs: " + numPairs);
			keyboard.nextLine();
			
			//initialize men and women arrays (0 for free, 1 for taken) and initialize Queue for men.
			//int[] men = new int[numPairs];
			int[] women = new int[numPairs];
			Queue<Integer> menQueue = new ArrayDeque<Integer>(numPairs);
			for (int j = 0; j < numPairs; j++) {
				menQueue.add(j);
			}
			
			
			ArrayList<ArrayList<Integer>> menMatr = new ArrayList<ArrayList<Integer>>();
			int[][] menProp = new int[numPairs][numPairs];
			ArrayList<ArrayList<Integer>> womenMatr = new ArrayList<ArrayList<Integer>>();
			
			ArrayList<Integer> matched = new ArrayList<Integer>();
			while(matched.size() < numPairs) matched.add(-1);
			for (int j = 0; j < matched.size(); j++) {
				System.out.print(matched.get(j)+" ");
			}
			System.out.println();
			//ArrayList<Integer> womenMatched = new ArrayList<Integer>();
			//while(womenMatched.size() < numPairs) womenMatched.add(0);
			
			
			
			//Set up Mens Matrix
			for (int j = 0; j < numPairs; j++) {		//row
				menMatr.add(new ArrayList<Integer>());
				for (int k = 0; k < numPairs; k++) { 	//column
					String token = keyboard.next();
					menMatr.get(j).add(Integer.parseInt(token));
					//System.out.println("W"+menMatr.get(j).get(k));
				}
				
			}
			

			
			//Set up Womens Matrix
			for (int j = 0; j < numPairs; j++) {		//row
				womenMatr.add(new ArrayList<Integer>());
				for (int k = 0; k < numPairs; k++) { 	//column
					String token = keyboard.next();
					womenMatr.get(j).add(Integer.parseInt(token));
					//System.out.println("M"+womenMatr.get(j).get(k));
				}
			
			}
			
			while (!menQueue.isEmpty()){
				//int bachelor = menQueue.peek();
				int bachelor = menQueue.remove();
				int luckyLady = -1;
				int done = 0;
				
				//find a girl that the bachelor hasn't proposed to
				for (int j = 0; j < numPairs && done == 0; j++) {
					if (menProp[bachelor][j] == 0) {
						menProp[bachelor][j] = 1; 
						luckyLady = menMatr.get(bachelor).get(j)-1;
						done = 1;
					}
				}
				//need to handle luckyLady = -1;
				if (women[luckyLady] == 0) {
					matched.set(bachelor, luckyLady);
					women[luckyLady] = 1;
					//men[bachelor] = 1;
					//menQueue.remove();
				}
				
				else if (womenMatr.get(luckyLady).indexOf(bachelor+1) < womenMatr.get(luckyLady).indexOf(matched.indexOf(luckyLady)+1)){
					//menQueue.remove();
					//men[bachelor] = 1;
					//men[matched.indexOf(luckyLady)] = 0;
					menQueue.add(matched.indexOf(luckyLady));
					matched.set(matched.indexOf(luckyLady), -1);
					matched.set(bachelor, luckyLady);
					
				}
				else menQueue.add(bachelor);
			}
			for (int j = 0; j < matched.size(); j++) {
				System.out.print(matched.get(j)+" ");
			}
			System.out.println();
			for (int j = 0; j < numPairs; j++) {
				System.out.print("W"+(matched.get(j)+1)+" ");
			}
			System.out.println();
		}
		
		keyboard.close();
	}

}
