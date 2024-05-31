package com.aerospike.timf;

import static org.apache.tinkerpop.gremlin.process.traversal.AnonymousTraversalSource.traversal;

import java.io.File;
import java.io.PrintWriter;
import java.io.StringWriter;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Random;
import java.util.Set;
import java.util.UUID;
import java.util.concurrent.ThreadLocalRandom;
import java.util.stream.Collectors;
import java.util.stream.Stream;

import org.apache.commons.cli.CommandLine;
import org.apache.commons.cli.CommandLineParser;
import org.apache.commons.cli.DefaultParser;
import org.apache.commons.cli.HelpFormatter;
import org.apache.commons.cli.Options;
import org.apache.commons.cli.ParseException;
import org.apache.tinkerpop.gremlin.driver.Cluster;
import org.apache.tinkerpop.gremlin.driver.remote.DriverRemoteConnection;
import org.apache.tinkerpop.gremlin.process.traversal.dsl.graph.GraphTraversalSource;
import org.apache.tinkerpop.gremlin.structure.T;

import com.aerospike.client.AerospikeClient;
import com.aerospike.client.Bin;
import com.aerospike.client.IAerospikeClient;
import com.aerospike.client.Key;
import com.aerospike.client.Record;
import com.aerospike.client.query.RecordSet;
import com.aerospike.client.query.Statement;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.github.javafaker.Faker;

public class DataLoader {
//    public static final String HOST = "172.17.0.3";
    public static final String GREMLIN_HOST = "127.0.0.1";
    public static final int GREMLIN_PORT = 8182;
    public static final int AEROSPIKE_PORT = 3000;
    public static final String AEROSPIKE_HOST = "127.0.0.1";
    private static final Cluster.Builder BUILDER = Cluster.build().addContactPoint(GREMLIN_HOST).port(GREMLIN_PORT).enableSsl(false);
    private static final String AEROSPIKE_NS = "retail-vector"; // "raw-data";
    private static final String AEROSPIKE_SET = "products"; // "fashion";
    private static final int NUM_USERS = 100_000;
    private final GraphTraversalSource g;
    private final IAerospikeClient client;
    
    // Similar products 1: Same gender, season, usage, brandName, different id
    // Similar products 2: Same brandName, usage, season, different subCategory, different id
    // Similar products 3: Same gender, usage, category, different season, different id
    private Map<String, Set<String>> similarIndex1 = new HashMap<>();
    private Map<String, Set<String>> similarIndex2 = new HashMap<>();
    private Map<String, Set<String>> similarIndex3 = new HashMap<>();
    
    private Set<String> validIds = new HashSet<>();

    public DataLoader(GraphTraversalSource g, IAerospikeClient client) {
        this.g = g;
        this.client = client;
    }
    
    private String formString(Record record, String ...bins) {
        StringBuilder sb = new StringBuilder();
        boolean first = true;
        for (String bin : bins) {
            if (!first) {
                sb.append('|');
            }
            first = false;
            Object binValue = record.getValue(bin);
            if(binValue != null) {
                sb.append(binValue.toString());
            }  
        }
        return sb.toString();
    }
    
    private void addToSet(Map<String, Set<String>> set, String key, String value) {
        Set<String> matches = set.get(key);
        if (matches == null) {
            matches = new HashSet<>();
            set.put(key, matches);
        }
        matches.add(value);
        
    }
    private void updateIndexes(Record record) {
        Object binValue = record.getValue("id");
        if(binValue == null) {
            return;
        }
        String id = binValue.toString();

        validIds.add(id);

        // Similar products 1: Same gender, season, usage, brandName, different id
        String index1Key = formString(record, "gender", "season", "usage", "brandName");
        addToSet(similarIndex1, index1Key, id);

        // Similar products 2: Same brandName, usage, season, different subCategory, different id
        String index2Key = formString(record, "brandName", "usage", "season");
        addToSet(similarIndex2, index2Key, id);

        // Similar products 3: Same gender, usage, category, different season, different id
        String index3Key = formString(record, "gender", "usage", "category");
        addToSet(similarIndex3, index3Key, id);
    }
    
    // Similar products 1: Same gender, season, usage, brandName, different id
    private int findSimilarProductsVariant1(String id, Record record, int count, Set<String> alreadyFound) {
        String key = formString(record, "gender", "season", "usage", "brandName");
        Set<String> matches = similarIndex1.get(key);

        // We use foundItems = 1 since this id is in the set of possible matches but it must be ignored
        int foundItems = 1;
        if (matches != null) {
            // This should always be the case as this id must match if nothing else!
            int size = matches.size();
            String[] matchesArray = matches.toArray(new String[0]);
            // While we have not found enough items and there are still items left to find...
            while (foundItems < (count+1) && size > foundItems) {
                int index = ThreadLocalRandom.current().nextInt(size);
                while (alreadyFound.contains(matchesArray[index])) {
                    index++; 
                    if (index >= matchesArray.length) {
                        index = 0;
                    }
                }
                String thisMatch = matchesArray[index];
                alreadyFound.add(thisMatch);
                foundItems++;
            }
        }
        return foundItems - 1;
    }
    
    private String getAttribute(String key, String name) {
        Record record = client.get(null, new Key(AEROSPIKE_NS, AEROSPIKE_SET, key), name);
        if (record != null) {
            return record.getString(name);
        }
        return "";
    }
    
    // Similar products 2: Same brandName, usage, season, different subCategory, different id
    private int findSimilarProductsVariant2(String id, Record record, int count, Set<String> alreadyFound) {
        String key = formString(record, "brandName", "usage", "season");
        String subcategory = record.getString("subCategory");
        Set<String> matches = similarIndex2.get(key);

        // We use foundItems = 1 since this id is in the set of possible matches but it must be ignored
        int foundItems = 1;
        if (matches != null) {
            // This should always be the case as this id must match if nothing else!
            String[] matchesArray = matches.toArray(new String[0]);
            int size = matchesArray.length;
            while (foundItems < (count+1)) {
                int index = ThreadLocalRandom.current().nextInt(size);
                int startIndex = index;
                while (alreadyFound.contains(matchesArray[index]) || getAttribute(matchesArray[index], "subCategory").equals(subcategory)) {
                    index++; 
                    if (index >= matchesArray.length) {
                        index = 0;
                    }
                    if (index == startIndex) {
                        // We have looped around, no more matches left
                        return foundItems - 1;
                    }
                }
                String thisMatch = matchesArray[index];
                alreadyFound.add(thisMatch);
                foundItems++;
            }
        }
        return foundItems - 1;
    }
    
    // Similar products 3: Same gender, usage, category, different season, different id
    private int findSimilarProductsVariant3(String id, Record record, int count, Set<String> alreadyFound) {
        String key = formString(record, "gender", "usage", "category");
        String season = record.getString("season");
        Set<String> matches = similarIndex3.get(key);

        // We use foundItems = 1 since this id is in the set of possible matches but it must be ignored
        int foundItems = 1;
        if (matches != null) {
            // This should always be the case as this id must match if nothing else!
            String[] matchesArray = matches.toArray(new String[0]);
            int size = matchesArray.length;
            while (foundItems < (count+1)) {
                int index = ThreadLocalRandom.current().nextInt(size);
                int startIndex = index;
                while (alreadyFound.contains(matchesArray[index]) || getAttribute(matchesArray[index], "season").equals(season)) {
                    index++; 
                    if (index >= matchesArray.length) {
                        index = 0;
                    }
                    if (index == startIndex) {
                        // We have looped around, no more matches left
                        return foundItems - 1;
                    }
                }
                String thisMatch = matchesArray[index];
                alreadyFound.add(thisMatch);
                foundItems++;
            }
        }
        return foundItems - 1;
    }
    
    private Set<String> findSimilarProducts(String id, int count) {
        Record record = client.get(null, new Key(AEROSPIKE_NS, AEROSPIKE_SET, id));
        Set<String> foundMatches = new HashSet<String>();
        Random rand = ThreadLocalRandom.current();
        int variant1 = rand.nextInt(count+1);
        int variant2 = 0;
        if (variant1 < count) {
            variant2 = rand.nextInt(count - variant1 + 1);
        }
        int variant3 = count - variant1 - variant2;
        findSimilarProductsVariant1(id, record, variant1, foundMatches); 
        findSimilarProductsVariant2(id, record, variant2, foundMatches); 
        findSimilarProductsVariant3(id, record, variant3, foundMatches); 
        return foundMatches;
    }
    
    public Set<String> listJsonFiles(String dir) {
        return Stream.of(new File(dir).listFiles())
          .filter(file -> !file.isDirectory())
          .map(File::getAbsolutePath)
          .filter(fileName -> fileName.endsWith(".json"))
          .collect(Collectors.toSet());
    }
    
    private void loadData(String dataPath) {
        System.out.println("Loading data...");
        client.truncate(null, AEROSPIKE_NS, AEROSPIKE_SET, null);
        Set<String> fileNames = listJsonFiles(dataPath);
        for (String filePath : fileNames) {
            try {
                File file = new File(filePath);
                String fileName = file.getName();
                int index = fileName.lastIndexOf('.');
                // Remove the filename suffix
                String id = fileName.substring(0, index);
                ObjectMapper mapper = new ObjectMapper();
                Map<String, ?> node = mapper.readValue(file, Map.class);
                node = (Map<String, ?>) node.get("data");
                List<String> colors = new ArrayList<>();
                colors.add((String)node.get("baseColour"));
                colors.add((String)node.get("colour1"));
                colors.add((String)node.get("colour2"));
                
                List<String> displayCat;
                if (node.get("displayCategories") == null) {
                    displayCat = new ArrayList<>();
                    displayCat.add("NA");
                }
                else {
                    displayCat = Arrays.asList(((String)node.get("displayCategories")).split(","));
                }
                Bin[] bins = new Bin[] {
                        new Bin("id", id),
                        new Bin("price", node.get("price")),
                        new Bin("salePrice", node.get("discountedPrice")),
                        new Bin("name", node.get("productDisplayName")),
                        new Bin("descriptors", node.get("productDescriptors")),
                        new Bin("variantName", node.get("variantName")),
                        new Bin("added", node.get("catalogAddDate")),
                        new Bin("brandName", node.get("brandName")),
                        new Bin("brandProfile", node.get("brandProfile")),
                        new Bin("ageGroup", node.get("ageGroup")),
                        new Bin("gender", node.get("gender")),
                        new Bin("colors", colors),
                        new Bin("season", node.get("season")),
                        new Bin("usage", node.get("usage")),
                        new Bin("articleAttr", node.get("articleAttributes")),
                        new Bin("images", node.get("styleImages")),
                        new Bin("displayCat", displayCat),
                        new Bin("category", ((Map<String, ?>)node.get("masterCategory")).get("typeName")),
                        new Bin("subCategory", ((Map<String, ?>)node.get("subCategory")).get("typeName")),
                        new Bin("articleType", ((Map<String, ?>)node.get("articleType")).get("typeName")),
                        new Bin("options", node.get("styleOptions")),
                };
                client.put(null, new Key(AEROSPIKE_NS, AEROSPIKE_SET, id), bins);
            }
            catch (Exception e) {
                System.out.printf("Ignoring file %s due to error %s (%s)\n", filePath, e.getMessage(), e.getClass().getName());
            }
        }
        System.out.println("Data load complete.");
    }
    
    private Object traverseMapPath(Map<String, Object> map, String ... paths) {
        try {
            Map<String, Object> current = map;
            for (String thisPath : paths) {
                if (current == null) {
                    return "";
                }
                Object value = current.get(thisPath);
                if (!(value instanceof Map)) {
                    return value;
                }
                else {
                    current = (Map<String, Object>) value;
                }
            }
            return current;
        }
        catch (Exception e) {
            return "";
        }
    }
    private void populateItemIntoGraph(Record record) {
        Map<String, Object> imageMap = (Map<String, Object>) record.getMap("images");
        String image_125x161 = (String) traverseMapPath(imageMap, "search", "resolutions", "125X161");
        String image_180X240 = (String) traverseMapPath(imageMap, "search", "resolutions", "180X240");
        
        Object binValue = record.getValue("id");
        if(binValue == null) {
            return;
        }
        String id = binValue.toString();

        g.addV("product")
            .property(T.id, id)
            .property("id", id)
            .property("name", record.getString("name"))
            .property("gender", record.getString("gender"))
            .property("usage", record.getString("usage"))
            .property("season", record.getString("season"))
            .property("brandName", record.getString("brandName"))
            .property("category", record.getString("category"))
            .property("subCategory", record.getString("subCategory"))
            .property("image_125X161", image_125x161)
            .property("image_180X240", image_180X240)
            .next();
    }
    
    public void scanData() {
        System.out.println("Scanning Aerospike database and populating graph");
        int count = 0;
        Statement stmt = new Statement();
        stmt.setNamespace(AEROSPIKE_NS);
        stmt.setSetName(AEROSPIKE_SET);
        RecordSet results = this.client.query(null, stmt);
        while (results.next()) {
            Record record = results.getRecord();
            updateIndexes(record);
            populateItemIntoGraph(record);
            if ((++count % 1000) == 0) {
                System.out.printf("   Done %,d\n", count);
            }
        }
        System.out.println("Done Scanning Aerospike database");
    }
    
    public void findMatches() {
        System.out.println("Populating customers and graph relationships...");
        String[] idList = validIds.toArray(new String[0]);
        Faker faker = new Faker();
        int edgesCreated = 0;
        Random random = ThreadLocalRandom.current();
        for (int i = 0; i < NUM_USERS; i++) {
            // Pick a random starting id
            String id = idList[random.nextInt(idList.length)];
            // Generate up to 12 edges, skewed towards the lower number
            int numEdgesToAdd = (1+random.nextInt(11) * random.nextInt(11)) /10;
            Set<String> results = findSimilarProducts(id, numEdgesToAdd);
            results.add(id);
            Object[] list = results.toArray();
            String name = faker.name().firstName();
            String uuid = UUID.randomUUID().toString();
            g.addV("customer")
                .property("id", uuid)
                .property(T.id, uuid)
                .property("firstName", name)
                .property("lastName", faker.name().lastName())
                .property("address", faker.address().streetAddress())
                .property("city", faker.address().city())
                .property("state", faker.address().stateAbbr())
                .property("zip", faker.address().zipCode())
                .as("customer")
                .V(list).addE("bought").from("customer").iterate();
            edgesCreated += results.size();
            
            if ((i+1) % 1000 == 0) {
                System.out.printf("%d%% done: %,d customers added, %,d edges formed\n",
                        (i*100)/NUM_USERS, i+1, edgesCreated);
            }
        }
        System.out.println("Customer population complete");
    }
    
    private static Options formOptions() {
        Options options = new Options();
        options.addOption("d",  "dataFolder", true, "Folder for loading JSON files into Aerospike. If this option is not present the data load phase is skipped");
        options.addOption("k", "keepGraph", false, "Keep the existing graph. If this is not specified, the graph database will be truncated before the data is loaded");
        return options;
    }
    
    private static void usage(Options options) {
        HelpFormatter formatter = new HelpFormatter();
        StringWriter sw = new StringWriter();
        PrintWriter pw = new PrintWriter(sw);
        String syntax = DataLoader.class.getName() + " [<options>]";
        formatter.printHelp(pw, 100, syntax, "options:", options, 0, 2, null);
        System.out.println(sw.toString());
        System.exit(1);

    }
    public static void main(String[] args) throws ParseException  {
        System.out.println("Creating the cluster");
        final Cluster cluster = BUILDER.create();

        System.out.println("Creating the GraphTraversalSource");
        final GraphTraversalSource g = traversal().withRemote(DriverRemoteConnection.using(cluster));
        
        DataLoader loader = new DataLoader(g, new AerospikeClient(AEROSPIKE_HOST, AEROSPIKE_PORT));

        Options options = formOptions();
        CommandLineParser parser = new DefaultParser();
        CommandLine cl = parser.parse(options, args, false);
        
        if (cl.hasOption("usage")) {
            usage(options);
        }
        if (cl.hasOption("dataFolder")) {
            loader.loadData(cl.getOptionValue("dataFolder"));
        }

        if (!cl.hasOption("keepGraph")) {
            System.out.println("Truncating graph database");
            // empty the database
            g.V().drop().iterate();
        }

        loader.scanData();
        loader.findMatches();
        cluster.close();
    }
}
