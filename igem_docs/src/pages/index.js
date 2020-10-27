import React from 'react';
import clsx from 'clsx';
import Layout from '@theme/Layout';
import Link from '@docusaurus/Link';
import useDocusaurusContext from '@docusaurus/useDocusaurusContext';
import useBaseUrl from '@docusaurus/useBaseUrl';
import styles from './styles.module.css';

const features = [
  {
    title: 'Accessible',
    imageUrl: 'img/iGEM_partnership.svg',
    description: (
      <>
        SOAP Lab was designed from the ground up to be easily accessible and
        used to get your liquid handlers up and running quickly how you need.
      </>
    ),
  },
  {
    title: 'Supporting communication',
    imageUrl: 'img/DBTL_red.svg',
    description: (
      <>
        Our entire project is based around the synthetic biology data standard
        SBOL to promote the sharing of genetic design data.
      </>
    ),
  },
  {
    title: 'End-to-end Validated',
    imageUrl: 'img/iGEM_digestion.svg',
    description: (
      <>
        We can vouch that our tool works - head over to our wiki to see how 
        we created our proof of concept (https://igem.org/Team:Imperial_College).
      </>
    ),
  },
];

function Feature({imageUrl, title, description}) {
  const imgUrl = useBaseUrl(imageUrl);
  return (
    <div className={clsx('col col--4', styles.feature)}>
      {imgUrl && (
        <div className="text--center">
          <img className={styles.featureImage} src={imgUrl} alt={title} />
        </div>
      )}
      <h3>{title}</h3>
      <p>{description}</p>
    </div>
  );
}

function Home() {
  const context = useDocusaurusContext();
  const {siteConfig = {}} = context;
  return (
    <Layout
      title={`Hello from ${siteConfig.title}`}
      description="Looks like you're reading our html! Description will go into a meta tag in <head />">
      <header className={clsx('hero hero--primary', styles.heroBanner)}>
        <div className="container">
          <h1 className="hero__title">Welcome to SOAP Lab!</h1>
          <p className="hero__subtitle">Official Imperial College iGEM 2020 Docs</p>
          <div className={styles.buttons}>
            <Link
              className={clsx(
                'button button--outline button--secondary button--lg',
                styles.getStarted,
              )}
              to={useBaseUrl('docs/')}>
              Get Started
            </Link>
          </div>
        </div>
      </header>
      <main>
        {features && features.length > 0 && (
          <section className={styles.features}>
            <div className="container">
              <div className="row">
                {features.map((props, idx) => (
                  <Feature key={idx} {...props} />
                ))}
              </div>              
            </div>
          </section>  
        )}
      </main>
    </Layout>
  );
}

export default Home;
