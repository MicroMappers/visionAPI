import java.io.File;
import java.io.FileInputStream;
//import java.io.FileNotFoundException;
import java.io.IOException;
import java.io.InputStream;
//import java.io.PrintWriter;
import java.nio.file.Files;
import java.nio.file.Paths;
import java.security.GeneralSecurityException;
import java.util.ArrayList;
//import java.util.List;

import com.google.vision.v1alpha1.Vision;
import com.google.vision.v1alpha1.VisionScopes;
import com.google.vision.v1alpha1.model.AnnotateImageRequest;
import com.google.vision.v1alpha1.model.BatchAnnotateImagesRequest;
import com.google.vision.v1alpha1.model.BatchAnnotateImagesResponse;
import com.google.vision.v1alpha1.model.Feature;
import com.google.vision.v1alpha1.model.Image;
import com.google.api.client.googleapis.auth.oauth2.GoogleCredential;
import com.google.api.client.googleapis.javanet.GoogleNetHttpTransport;
import com.google.api.client.http.javanet.NetHttpTransport;
import com.google.api.client.json.JsonFactory;
//import com.google.api.client.json.JsonObjectParser;
//import com.google.api.client.json.gson.GsonFactory;
import com.google.api.client.json.jackson2.JacksonFactory;
import com.google.common.collect.Lists;


public class VisionApi {

	public static void main(String[] args) {
		String key, path;

		if(args.length != 2)
		{
			System.out.println("Please specify credentials file path and image directory path");
		}
		else
		{
			key = args[0];
			path = args[1];
			ArrayList<String> imagePaths = new ArrayList<String>();

			File dirList = new File(path);
			File[] directoryListing = dirList.listFiles();
			if (directoryListing != null) {
				for (File child : directoryListing) {
					if(child.getName().toLowerCase().contains(".jpg"))
					{
						imagePaths.add(child.getAbsolutePath());
					}
				}
				System.out.println(imagePaths.size());
				for(String img : imagePaths)
				{
					generateVisionJson(img,key);
				}
			}
		}

	}

	private static void generateVisionJson(String imgpath, String keyPath) {
		Vision vision = null;
		GoogleCredential credential = null;
		InputStream credentialsStream = null;
		NetHttpTransport ht;
		try {
			ht = GoogleNetHttpTransport.newTrustedTransport();
			JsonFactory jf = JacksonFactory.getDefaultInstance();
			
			credentialsStream = new FileInputStream(keyPath);
			credential = GoogleCredential.fromStream(credentialsStream, ht, jf).createScoped(VisionScopes.all());
			
			vision = new Vision(ht, jf, credential);
		} catch (GeneralSecurityException e2) {
			// TODO Auto-generated catch block
		} catch(IOException e){
			e.printStackTrace();
		}finally{
			if (credentialsStream != null) {
				try {
					credentialsStream.close();
				} catch (IOException e) {
					// TODO Auto-generated catch block
					e.printStackTrace();
				}
			}
		}

		if(vision != null)
		{
			try
			{
				//System.out.println(imgpath);
				Image image = new Image().encodeContent(Files.readAllBytes(Paths.get(imgpath)));//readFileToBytes(wiki_path));

				BatchAnnotateImagesRequest content = new BatchAnnotateImagesRequest();

				AnnotateImageRequest annotatedImageReq = new AnnotateImageRequest();
				annotatedImageReq.setFeatures(Lists.newArrayList(labelDetection(), textDetection(), landmarkDetection()));
				annotatedImageReq.setImage(image);
				content.setRequests(Lists.newArrayList(annotatedImageReq));

				//PrintWriter out = new PrintWriter("/tmp/test.json");
				//out.println(Lists.newArrayList(annotatedImageReq));

				//out.close();

				//System.out.println(annotatedImageReq.toPrettyString());

				BatchAnnotateImagesResponse response = vision.images().annotate(content).execute();

				/*BatchAnnotateImagesRequest content = new BatchAnnotateImagesRequest();

				Feature textDetection = new Feature();
				textDetection.setType("TEXT_DETECTION");
				textDetection.setMaxResults(1);

				List<Feature> featureList = Lists.newArrayList();//new ArrayList<Feature>();
				featureList.add(textDetection);

				List<AnnotateImageRequest> anImgReqList = Lists.newArrayList();//new ArrayList<AnnotateImageRequest>();

				AnnotateImageRequest annotatedImageReq = new AnnotateImageRequest();
				annotatedImageReq.setFeatures(featureList);
				annotatedImageReq.setImage(image);
				anImgReqList.add(annotatedImageReq);
				content.setRequests(anImgReqList);

				BatchAnnotateImagesResponse response = vision.images().annotate(content).execute();*/

				if(response.getResponses() == null || response.getResponses().get(0) == null
						|| response.getResponses().get(0).getTextAnnotations() == null
						|| response.getResponses().get(0).getTextAnnotations().get(0) == null
						|| response.getResponses().get(0).getTextAnnotations().get(0).getDescription() == null){
					System.out.println("response null");
				}
				else
					System.out.println(response.getResponses().get(0).getTextAnnotations().get(0).getDescription());
					System.out.println(response.getResponses().get(0).getLabelAnnotations());
			} catch (IOException e) {
				// TODO Auto-generated catch block
				e.printStackTrace();
			}
		}
		//return response.getResponses().get(0).getTextAnnotations().get(0).getDescription();
	}

	private static Feature landmarkDetection() {
		Feature textDetection = new Feature();
		textDetection.setType("LANDMARK_DETECTION");
		textDetection.setMaxResults(1);
		return textDetection;
	}

	private static Feature textDetection() {
		Feature textDetection = new Feature();
		textDetection.setType("TEXT_DETECTION");
		textDetection.setMaxResults(10);
		return textDetection;
	}

	private static Feature labelDetection() {
		Feature textDetection = new Feature();
		textDetection.setType("LABEL_DETECTION");
		textDetection.setMaxResults(10);
		return textDetection;
	}

	/*private static byte[] readFileToBytes(File f) {
		int size = (int) f.length();
		byte bytes[] = new byte[size];
		byte tmpBuff[] = new byte[size];
		FileInputStream fis = null;
		try {
			fis = new FileInputStream(f);
			int read = fis.read(bytes, 0, size);
			if (read < size) {
				int remain = size - read;
				while (remain > 0) {
					read = fis.read(tmpBuff, 0, remain);
					System.arraycopy(tmpBuff, 0, bytes, size - remain, read);
					remain -= read;
				}
			}
		}
		catch (FileNotFoundException e)
		{
			e.printStackTrace();;
		}
		catch (IOException e){
			e.printStackTrace();
		} finally {
			try {
				if(fis != null)
					fis.close();
			} catch (IOException e) {
				// TODO Auto-generated catch block
				e.printStackTrace();
			}
		}

		return bytes;
	}*/

}
