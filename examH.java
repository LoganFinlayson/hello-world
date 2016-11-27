import java.util.ArrayList;
import java.util.HashMap;
import java.util.LinkedList;
import java.util.List;
import java.util.Map;
import java.util.Queue;
import java.util.Scanner;

public class examH {

	private static int numTests, numQdb, numQex; //Number of tests, database Q's and exam Q's.
	
	public static Map<String, Integer> DvertexNumbers, TvertexNumbers, DvertexFreq, TvertexFreq;
	//public static Map<String, Integer> vertexFreq;
	public static int[] parent;
	
	
	public static void main(String[] args) {
		Scanner keyboard = new Scanner(System.in);
		numTests = keyboard.nextInt();
		keyboard.useDelimiter("[ \r\n]+");
		
		keyboard.nextLine();
		//System.out.println("Number of tests: " + numTests);
		
		for (int i = 0; i < numTests; i++) {
			
			numQdb = keyboard.nextInt();
			numQex = keyboard.nextInt();
			
			DvertexNumbers = new HashMap<String, Integer>();
			TvertexNumbers = new HashMap<String, Integer>();
			DvertexFreq = new HashMap<String, Integer>();
			TvertexFreq = new HashMap<String, Integer>();
			
			//System.out.println("Number of db Q's: " + numQdb);
			//System.out.println("Number of exam Q's: " + numQex);
			
			keyboard.nextLine(); //Getting to Difficulty line
			
			//System.out.println("Difficulties:");
			
			int numDiff = 0;
			List<String> diffList = new ArrayList<String>();
			String vertex;
			for (int j = 0; j < numQex; j++) {
				vertex = keyboard.next();
				if (DvertexNumbers.containsKey(vertex)) {
					DvertexFreq.put(vertex, DvertexFreq.get(vertex) + 1);
				}
				else {
					diffList.add(vertex);
					numDiff++;
					DvertexNumbers.put(vertex, numDiff);
					DvertexFreq.put(vertex, 1);
				}
			}
			
			List<String> topicList = new ArrayList<String>();
			int numTopic = 0;
			//System.out.println("Topics:");
			for (int j = 0; j < numQex; j++){
				vertex = keyboard.next();
				if (TvertexNumbers.containsKey(vertex)) {
					TvertexFreq.put(vertex, TvertexFreq.get(vertex) + 1);
				}
				else {
					topicList.add(vertex);
					numTopic++;
					TvertexNumbers.put(vertex, numDiff + numTopic);
					TvertexFreq.put(vertex, 1);
				}
			}
			
			//set up graph
			int graphsize = DvertexNumbers.size() + TvertexNumbers.size() + 2;
			int[][] graph = new int[graphsize][graphsize];
			//System.out.println("is vertexNumbers.size() equal to numpDiff + numTop?");
			//System.out.println(graphsize - 2 == (numDiff + numTopic));
			//for (int j = 0; j < graphsize; j++) {	}
			for (String v : diffList){
				graph[0][DvertexNumbers.get(v)] = DvertexFreq.get(v);
			}
			for (String v : topicList){
				graph[TvertexNumbers.get(v)][graphsize - 1] = TvertexFreq.get(v);
			}
			
			
			keyboard.nextLine(); //Getting to database questions
			
			String diff;
			String topic;
			for (int j = 0; j < numQdb; j++) {
				keyboard.next(); //skip name
				topic = keyboard.next();
				diff = keyboard.next();
				try{
					graph[DvertexNumbers.get(diff)][TvertexNumbers.get(topic)] += 1;
				} catch (NullPointerException e) { 
					//System.out.println("failed: " + topic + " " + diff);
				}
				//System.out.println("Put " + diff + ", " + topic + " at " + vertexNumbers.get(diff) + ", " + vertexNumbers.get(topic));
				keyboard.nextLine();
			}
			
			int[][] residualGraph = new int[graphsize][graphsize];
			for (int j = 0; j < graphsize; j++) {
				for (int k = 0; k < graphsize; k++){
					residualGraph[j][k] = graph[j][k];
				}
			}
			
			//System.out.println(Arrays.deepToString(graph));
			//System.out.println(Arrays.deepToString(residualGraph));
			
			int pathFlow, u, v;
			int maxFlow = 0;
			int destination = graphsize - 1;
			parent = new int[residualGraph.length];
			
			while (BFS(0, destination, residualGraph)) {
	            pathFlow = Integer.MAX_VALUE;
	            for (v = destination; v != 0; v = parent[v]) {
	                u = parent[v];
	                pathFlow = Math.min(pathFlow, residualGraph[u][v]);
	            }
	            for (v = destination; v != 0; v = parent[v]) {
	                u = parent[v];
	                residualGraph[u][v] -= pathFlow;
	                residualGraph[v][u] += pathFlow;
	            }
	            maxFlow += pathFlow;	
	        }
			
			
	        //System.out.println("Maxflow: " + maxFlow);
			
	        if (maxFlow >= numQex) {
	        	System.out.println("Yes");
	        }
	        else {
	        	System.out.println("No");
	        }
		}
		
		
		keyboard.close();
	}
	
	public static boolean BFS(int source, int sink, int graph[][]) {
        
		boolean pathFound = false;
        
        int destination; 
        int node;
        
        boolean[] visited = new boolean[graph.length];
        Queue<Integer> queue = new LinkedList<Integer>();
 
        for (int vertex = 0; vertex < graph.length; vertex++) {
            parent[vertex] = -1;
            visited[vertex] = false;
        }
 
        queue.add(source);
        parent[source] = -1;
        visited[source] = true;
 
        while (!queue.isEmpty()) { 
            node = queue.remove();
            destination = 1;
 
            while (destination < graph.length) {
                if (graph[node][destination] > 0 && !visited[destination]) {
                    parent[destination] = node;
                    queue.add(destination);
                    visited[destination] = true;
                }
                destination++;
            }
        }
        if(visited[sink]) {
            pathFound = true;
        }
        return pathFound;
    }
	
	

}
