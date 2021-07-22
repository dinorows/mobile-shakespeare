import React from 'react'
import Paper from '@material-ui/core/Paper'
import ReactMarkdown from 'react-markdown'
import 'github-markdown-css'

const AboutPage = () => {
  const markdown = `
  # Lorem Ipsum
  ## Lorem Ipsum

  **L**orem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor 
  incididunt ut labore et dolore magna aliqua. Leo vel orci porta non. Enim facilisis 
  gravida neque convallis a. Consequat semper viverra nam libero justo laoreet sit. 
  Vulputate dignissim suspendisse in est ante. Augue neque gravida in fermentum et 
  sollicitudin ac. _Semper eget duis at tellus at urna condimentum_. Varius vel pharetra 
  vel turpis nunc eget lorem dolor sed. Fringilla urna porttitor rhoncus dolor purus non 
  enim praesent. Tortor aliquam nulla facilisi cras fermentum odio. Morbi tristique 
  senectus et netus et malesuada fames ac turpis. Tellus rutrum tellus pellentesque eu.
   Mattis aliquam faucibus purus in massa tempor. Viverra ipsum nunc aliquet bibendum enim 
   facilisis gravida neque. Purus sit amet volutpat consequat mauris nunc.
  
  **S**it amet consectetur adipiscing elit pellentesque habitant morbi. Tincidunt id aliquet 
  risus feugiat in ante. Metus dictum at tempor commodo ullamcorper a lacus vestibulum sed. 
  Risus pretium quam vulputate dignissim suspendisse in est ante. Sagittis orci a 
  scelerisque purus. Sagittis id consectetur purus ut faucibus pulvinar elementum. Tellus 
  rutrum tellus pellentesque eu tincidunt. Ut enim blandit volutpat maecenas volutpat. 
  Adipiscing enim eu turpis egestas pretium aenean pharetra magna ac. Aliquet lectus proin 
  nibh nisl condimentum. _Sagittis purus sit amet volutpat consequat mauris_. Commodo elit at 
  imperdiet dui accumsan. Amet risus nullam eget felis eget nunc lobortis mattis. Ut 
  porttitor leo a diam sollicitudin tempor id eu nisl. Non tellus orci ac auctor augue 
  mauris. Nunc congue nisi vitae suscipit. Nam aliquam sem et tortor consequat id. Auctor 
  augue mauris augue neque gravida in fermentum et sollicitudin. Magna fermentum iaculis 
  eu non diam phasellus vestibulum lorem sed.
  
 **N**unc consequat interdum varius sit amet. Amet risus nullam eget felis eget nunc. Nunc 
  scelerisque viverra mauris in. Leo vel orci porta non. Pharetra pharetra massa massa 
  ultricies. Ultrices gravida dictum fusce ut placerat. Morbi tristique senectus et netus. 
  Arcu dui vivamus arcu felis bibendum ut. _Amet venenatis urna cursus eget nunc_. Quam 
  lacus suspendisse faucibus interdum posuere lorem ipsum. Morbi blandit cursus risus at 
  ultrices mi tempus imperdiet. Est velit egestas dui id ornare arcu. 
  `;

  return (
    <Paper>
        <div style={{ backgroundColor: 'white', padding: 12 }}>
          <ReactMarkdown
            className="markdown-body"
            source={markdown}
            escapeHtml={true}
          />
        </div>
    </Paper>
  )
}
export default AboutPage
